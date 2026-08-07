from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING
from unittest.mock import call, sentinel

import pytest

import iconeval._dependencies
import iconeval._job
import iconeval.main
from iconeval.main import icon_evaluation, main

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import Mock

    import pytest_mock
    from pytest_datadir.plugin import LazyDataDir
    from pytest_mock import MockerFixture

    from tests.integration import OutputDirRegression


@pytest.fixture(autouse=True)
def mocked_subprocess__dependencies(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._dependencies, "subprocess", autospec=True)
    mock.run.return_value.returncode = 0
    return mock


@pytest.fixture(autouse=True)
def mocked_subprocess__job(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._job, "subprocess", autospec=True)
    mock.Popen.return_value.returncode = 0
    mock.Popen.return_value.poll.return_value = 0
    mock.Popen.return_value.communicate.return_value = ("stdout", "stderr")
    mock.PIPE = sentinel.PIPE
    return mock


def test_main(mocker: pytest_mock.MockerFixture) -> None:
    mocked_logger = mocker.patch.object(iconeval.main, "logger")
    mocked_fire = mocker.patch.object(iconeval.main, "fire")
    main()
    mocked_logger.remove.assert_called_once_with()
    mocked_fire.Fire.assert_called_once_with(icon_evaluation)


@pytest.mark.parametrize("tags", [[], None])
def test_icon_evaluation_single_input_success(
    tags: list[str] | None,
    output_dir_regression: OutputDirRegression,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    obtained_dir = icon_evaluation(
        tmp_input_dir,
        output_dir=tmp_output_dir,
        tags=tags,
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=16",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
        ]
        if "portrait_plot" in recipe.stem:
            cmd.append("--max_parallel_tasks=1")
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_not_called()

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_multi_input_success(
    output_dir_regression: OutputDirRegression,
    tmp_input_dirs: list[Path],
    tmp_output_dir: Path,
    recipe_template_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    obtained_dir = icon_evaluation(
        *tmp_input_dirs,
        publish_html=True,
        html_name="my_html_name",
        recipe_templates=[
            recipe_template_dir / "recipe_basics_*.yml",
            recipe_template_dir / "recipe_ocean_*.yml",
            recipe_template_dir / "recipe_portrait_plot.yml",
        ],
        log_level="debug",
        output_dir=tmp_output_dir,
        path_templates=["my_icon_sim.yml", "{var_type}/my_{exp}_of_icon_xpp*.nc"],
        account="Slurm_account",
        esmvaltool_executable="ESMValTool executable",
        srun_executable="srun executable",
        ignore_recipe_esmvaltool_options=True,
        ignore_recipe_srun_options=True,
        ignore_recipe_dask_options=True,
        esmvaltool_options={"--auxiliary_data_dir": "/path/to/a"},
        srun_options={"--cpus-per-task": 17},
        dask_options={"--n_workers": 17},
        tags=["map", "subdaily", "!annual-cycle", "portrait-plot", "!ocean"],
        timerange="19990101/20000101",
        ugrid=False,
    )

    # Check output
    assert obtained_dir.name == "my_html_name_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "ESMValTool executable"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun executable"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun executable",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=17",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=Slurm_account",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "ESMValTool executable",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
            "--auxiliary_data_dir=/path/to/a",
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_called_once_with(
        "url/to/swift_storage/my_folder",
        "this_is_a_very_nice_token",
    )
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "this_is_a_very_nice_token",
            "os_storage_url": "url/to/swift_storage/my_folder",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="iconeval"),
        call(container="iconeval", options={"read_acl": ".r:*"}),
    ]
    assert mocked_service_instance.upload.call_count == 1
    upload_call = mocked_service_instance.upload.mock_calls[0]
    assert upload_call.args == ()
    assert len(upload_call.kwargs) == 2  # noqa: PLR2004
    assert upload_call.kwargs["container"] == "iconeval"
    objects_to_upload = [
        (
            str(obtained_dir / "esmvaltool_output" / f.name),
            f"my_html_name/{f.name}",
        )
        for f in (output_dir_regression.expected_dir / "esmvaltool_output").iterdir()
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)

    # Check logging output
    for input_dir in tmp_input_dirs:
        assert f"- {input_dir.stem}" in caplog.text
        assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_single_input_background(
    output_dir_regression: OutputDirRegression,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    recipe_template_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("SLURM_JOB_ACCOUNT", "custom_slurm_account")

    obtained_dir = icon_evaluation(
        tmp_input_dir,
        recipe_templates=recipe_template_dir / "recipe_basics_timeseries.yml",
        output_dir=tmp_output_dir,
        path_templates="my_icon_sim.yml",
        background=True,
        dask=False,
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(
        obtained_dir,
        empty_subdirs=["esmvaltool_output", "slurm"],
    )

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    mocked_subprocess__job.Popen.return_value.communicate.assert_not_called()
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--account=custom_slurm_account",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_not_called()

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" not in caplog.text


def test_icon_evaluation_single_input_fail(
    output_dir_regression: OutputDirRegression,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    recipe_template_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocked_subprocess__job.Popen.return_value.returncode = 42
    mocked_subprocess__job.Popen.return_value.poll.return_value = 42

    obtained_dir = icon_evaluation(
        tmp_input_dir,
        publish_html=True,
        recipe_templates=str(recipe_template_dir / "recipe_basics_timeseries.yml"),
        output_dir=tmp_output_dir,
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=16",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_called_once_with(
        "url/to/swift_storage/my_folder",
        "this_is_a_very_nice_token",
    )
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "this_is_a_very_nice_token",
            "os_storage_url": "url/to/swift_storage/my_folder",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="iconeval"),
        call(container="iconeval", options={"read_acl": ".r:*"}),
    ]
    assert mocked_service_instance.upload.call_count == 1
    upload_call = mocked_service_instance.upload.mock_calls[0]
    assert upload_call.args == ()
    assert len(upload_call.kwargs) == 2  # noqa: PLR2004
    assert upload_call.kwargs["container"] == "iconeval"
    objects_to_upload = [
        (
            str(obtained_dir / "esmvaltool_output" / f.name),
            f"{obtained_dir.name}/{f.name}",
        )
        for f in (output_dir_regression.expected_dir / "esmvaltool_output").iterdir()
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[-] Job {recipe.stem} failed with code 42" in caplog.text


def test_icon_evaluation_single_input_run_longer(
    output_dir_regression: OutputDirRegression,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    recipe_template_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Let one job wait for a sec, the other finish immediately
    mocked_subprocess__job.Popen.return_value.poll.side_effect = [
        None,  # call to is_running of first job within _run_jobs
        1,  # call to is_running of second job within _run_jobs
        1,  # call to is_running of second job within job_status
        1,  # call to is_successful of second job within job_status
        1,  # call to is_successful of second job within _run_jobs
        0,  # call to is_running of first job within _run_jobs
        0,  # call to is_running of first job within job_status
        0,  # call to is_successful of first job within job_status
        0,  # call to is_successful of first job within _run_jobs
        1,  # call to is_running of second job within _run_jobs
        None,  # call to is_running of first job within finally block
        1,  # call to is_running of second job within finally block
    ]

    obtained_dir = icon_evaluation(
        tmp_input_dir,
        recipe_templates=[
            str(recipe_template_dir / "recipe_basics_timeseries.yml"),
            recipe_template_dir / "recipe_basics_maps.yml",
        ],
        output_dir=tmp_output_dir,
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_called_once_with()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=16",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
        ]
        if "portrait_plot" in recipe.stem:
            cmd.append("--max_parallel_tasks=1")
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_not_called()

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    assert "[-] Job recipe_basics_timeseries failed with code 0" in caplog.text
    assert "[+] Job recipe_basics_maps finished successfully" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )


def test_icon_evaluation_single_input_custom_recipe_options(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    obtained_dir = icon_evaluation(
        tmp_input_dir,
        recipe_templates=lazy_shared_datadir / "recipe_basics_zonal_mean_lines.yml",
        always_use_default_recipe_templates=True,
        output_dir=tmp_output_dir,
        tags="_custom_tag_",
        project="EMAC",
        dataset="EMAC",
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=64",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
            "--max_parallel_tasks=1",
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_not_called()

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_single_input_custom_recipe_options_ignore(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    obtained_dir = icon_evaluation(
        tmp_input_dir,
        recipe_templates=[
            lazy_shared_datadir / "recipe_basics_zonal_mean_lines.yml",
            lazy_shared_datadir / "recipe_basics_maps.yml",
        ],
        output_dir=tmp_output_dir,
        ignore_recipe_esmvaltool_options=True,
        ignore_recipe_srun_options=True,
        ignore_recipe_dask_options=True,
        tags="!map",
    )

    # Check output
    assert obtained_dir.name == "input_20000101_000000UTC"
    output_dir_regression.check(obtained_dir, empty_subdirs=["slurm"])

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((output_dir_regression.expected_dir / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    mocked_subprocess__job.Popen.return_value.terminate.assert_not_called()
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=16",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={obtained_dir / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(obtained_dir / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(obtained_dir / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_not_called()

    # Check logging output
    assert f"- {tmp_input_dir.stem}" in caplog.text
    assert f"(Path: {tmp_input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {obtained_dir / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_empty_input_dir_fail(tmp_output_dir: Path) -> None:
    msg = r"No input directory given"
    with pytest.raises(ValueError, match=re.escape(msg)):
        icon_evaluation(output_dir=tmp_output_dir)


def test_icon_evaluation_invalid_input_dir_fail(
    tmp_input_dir: Path,
    tmp_output_dir: Path,
) -> None:
    tmp_input_dir.rmdir()
    msg = r"does not exist"
    with pytest.raises(NotADirectoryError, match=re.escape(msg)):
        icon_evaluation(tmp_input_dir, output_dir=tmp_output_dir)


def test_icon_evaluation_invalid_exps_fail(
    tmp_input_dirs: list[Path],
    tmp_output_dir: Path,
) -> None:
    input_dirs = [d / "exp" for d in tmp_input_dirs]
    for input_dir in input_dirs:
        input_dir.mkdir(parents=True, exist_ok=True)
    msg = r"Multiple experiments with the same name are not supported"
    with pytest.raises(ValueError, match=re.escape(msg)):
        icon_evaluation(*input_dirs, output_dir=tmp_output_dir)


def test_icon_evaluation_invalid_recipe_template_fail(
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    tmp_path: Path,
) -> None:
    msg = r"No recipe template matching"
    with pytest.raises(FileNotFoundError, match=re.escape(msg)):
        icon_evaluation(
            tmp_input_dir,
            output_dir=tmp_output_dir,
            recipe_templates=tmp_path / "non_existing_recipe.yml",
        )


@pytest.mark.parametrize(
    ("tags", "error_msg"),
    [
        (None, r"No recipe templates given"),
        ("tag", r"No recipe templates for tags ['tag'] given"),
        (["t1", "!t2"], r"No recipe templates for tags ['t1', '!t2'] given"),
    ],
)
def test_icon_evaluation_invalid_no_recipe_templates_fail(
    tags: list[str] | None,
    error_msg: str,
    tmp_input_dir: Path,
    tmp_output_dir: Path,
) -> None:
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        icon_evaluation(
            tmp_input_dir,
            output_dir=tmp_output_dir,
            recipe_templates=[],
            tags=tags,
        )


def test_icon_evaluation_invalid_recipe_template_invalid_glob_fail(
    tmp_input_dir: Path,
    tmp_output_dir: Path,
    tmp_path: Path,
) -> None:
    msg = r"No recipe template matching"
    with pytest.raises(FileNotFoundError, match=re.escape(msg)):
        icon_evaluation(
            tmp_input_dir,
            output_dir=tmp_output_dir,
            recipe_templates=tmp_path / "*.yml",
        )
