from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING
from unittest.mock import call, sentinel

import pytest

import iconeval._dependencies
import iconeval._job
import iconeval.main
import iconeval.output_handling.publish_html
from iconeval.main import icon_evaluation, main
from tests.integration import assert_output

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import Mock

    import pytest_mock
    from pytest_mock import MockerFixture


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
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        log_file=None,
        output_dir=output_dir,
        tags=tags,
    )

    # Check output
    expected_output = expected_output_dir / "test_icon_evaluation_single_input_success"
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        if "portrait_plot" in recipe.stem:
            cmd.append("--max_parallel_tasks=1")
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_multi_input_success(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    recipe_template_dir: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
) -> None:
    input_dirs = [tmp_path / "input_1", tmp_path / "input_2"]
    output_dir = tmp_path / "output"
    for input_dir in input_dirs:
        input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        *input_dirs,
        publish_html=True,
        html_name="my_html_name",
        recipe_templates=[
            recipe_template_dir / "recipe_basics_*.yml",
            recipe_template_dir / "recipe_ocean_*.yml",
            recipe_template_dir / "recipe_portrait_plot.yml",
        ],
        log_level="debug",
        log_file=None,
        output_dir=output_dir,
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
    expected_output = expected_output_dir / "test_icon_evaluation_multi_input_success"
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )

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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "ESMValTool executable",
            "run",
            str(actual_output / "recipes" / recipe.name),
            "--auxiliary_data_dir=/path/to/a",
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
            str(actual_output / "esmvaltool_output" / f.name),
            f"my_html_name/{f.name}",
        )
        for f in (expected_output / "esmvaltool_output").iterdir()
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)

    # Check logging output
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_single_input_background(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    recipe_template_dir: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SLURM_JOB_ACCOUNT", "custom_slurm_account")

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        recipe_templates=recipe_template_dir / "recipe_basics_timeseries.yml",
        log_file=None,
        output_dir=output_dir,
        background=True,
        dask=False,
    )

    # Check output
    expected_output = (
        expected_output_dir / "test_icon_evaluation_single_input_background"
    )
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["esmvaltool_output", "slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" not in caplog.text


def test_icon_evaluation_single_input_fail(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    recipe_template_dir: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
) -> None:
    mocked_subprocess__job.Popen.return_value.returncode = 42
    mocked_subprocess__job.Popen.return_value.poll.return_value = 42

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        publish_html=True,
        recipe_templates=str(recipe_template_dir / "recipe_basics_timeseries.yml"),
        log_file=None,
        output_dir=output_dir,
    )

    # Check output
    expected_output = expected_output_dir / "test_icon_evaluation_single_input_fail"
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
            str(actual_output / "esmvaltool_output" / f.name),
            f"{actual_output.name}/{f.name}",
        )
        for f in (expected_output / "esmvaltool_output").iterdir()
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)

    # Check logging output
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[-] Job {recipe.stem} failed with code 42" in caplog.text


def test_icon_evaluation_single_input_run_longer(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    recipe_template_dir: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
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

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        recipe_templates=[
            str(recipe_template_dir / "recipe_basics_timeseries.yml"),
            recipe_template_dir / "recipe_basics_maps.yml",
        ],
        log_file=None,
        output_dir=output_dir,
    )

    # Check output
    expected_output = (
        expected_output_dir / "test_icon_evaluation_single_input_run_longer"
    )
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        if "portrait_plot" in recipe.stem:
            cmd.append("--max_parallel_tasks=1")
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    assert "[-] Job recipe_basics_timeseries failed with code 0" in caplog.text
    assert "[+] Job recipe_basics_maps finished successfully" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )


def test_icon_evaluation_single_input_custom_recipe_options(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        recipe_templates=sample_data_path
        / "recipe_templates"
        / "recipe_basics_zonal_mean_lines.yml",
        always_use_default_recipe_templates=True,
        log_file=None,
        output_dir=output_dir,
        tags="_custom_tag_",
        project="EMAC",
        dataset="EMAC",
    )

    # Check output
    expected_output = (
        expected_output_dir / "test_icon_evaluation_single_input_custom_recipe_options"
    )
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
            "--max_parallel_tasks=1",
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_single_input_custom_recipe_options_ignore(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(
        input_dir,
        recipe_templates=[
            sample_data_path
            / "recipe_templates"
            / "recipe_basics_zonal_mean_lines.yml",
            sample_data_path / "recipe_templates" / "recipe_basics_maps.yml",
        ],
        log_file=None,
        output_dir=output_dir,
        ignore_recipe_esmvaltool_options=True,
        ignore_recipe_srun_options=True,
        ignore_recipe_dask_options=True,
        tags="!map",
    )

    # Check output
    expected_output = (
        expected_output_dir
        / "test_icon_evaluation_single_input_custom_recipe_options_ignore"
    )
    assert_output(
        tmp_path,
        actual_output,
        expected_output,
        empty_dirs=["slurm"],
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
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

    recipes = list((expected_output / "recipes").glob("*.yml"))
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
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
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
    assert f"- {input_dir.stem}" in caplog.text
    assert f"(Path: {input_dir})" in caplog.text
    for recipe in recipes:
        assert (
            f"- Job {recipe.stem} (Log: {actual_output / 'slurm' / recipe.stem}.log)"
            in caplog.text
        )
        assert f"[+] Job {recipe.stem} finished successfully" in caplog.text


def test_icon_evaluation_empty_input_dir_fail(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    msg = r"No input directory given"
    with pytest.raises(ValueError, match=re.escape(msg)):
        icon_evaluation(log_file=None, output_dir=output_dir)


def test_icon_evaluation_invalid_input_dir_fail(tmp_path: Path) -> None:
    input_dir = tmp_path / "this_dir_does_not_exist"
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    msg = r"does not exist"
    with pytest.raises(NotADirectoryError, match=re.escape(msg)):
        icon_evaluation(input_dir, log_file=None, output_dir=output_dir)


def test_icon_evaluation_invalid_exps_fail(tmp_path: Path) -> None:
    input_dirs = [
        tmp_path / "input_1" / "exp",
        tmp_path / "input_2" / "exp",
    ]
    for input_dir in input_dirs:
        input_dir.mkdir(parents=True, exist_ok=True)
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    msg = r"Multiple experiments with the same name are not supported"
    with pytest.raises(ValueError, match=re.escape(msg)):
        icon_evaluation(*input_dirs, log_file=None, output_dir=output_dir)


def test_icon_evaluation_invalid_recipe_template_fail(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    msg = r"No recipe template matching"
    with pytest.raises(FileNotFoundError, match=re.escape(msg)):
        icon_evaluation(
            input_dir,
            log_file=None,
            output_dir=output_dir,
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
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        icon_evaluation(
            input_dir,
            log_file=None,
            output_dir=output_dir,
            recipe_templates=[],
            tags=tags,
        )


def test_icon_evaluation_invalid_recipe_template_invalid_glob_fail(
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    msg = r"No recipe template matching"
    with pytest.raises(FileNotFoundError, match=re.escape(msg)):
        icon_evaluation(
            input_dir,
            log_file=None,
            output_dir=output_dir,
            recipe_templates=tmp_path / "*.yml",
        )
