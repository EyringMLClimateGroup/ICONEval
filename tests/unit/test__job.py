from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING
from unittest.mock import sentinel

import pytest

from iconeval._config import ESMValToolConfig
from iconeval._job import Job
from iconeval._recipe import Recipe

if TYPE_CHECKING:
    from pathlib import Path

    import pytest_mock


@pytest.fixture
def sentinel_job() -> Job:
    return Job(
        recipe=sentinel.recipe,
        esmvaltool_config=sentinel.esmvaltool_config,
        account=sentinel.account,
        esmvaltool_executable=sentinel.esmvaltool_executable,
        srun_executable=sentinel.srun_executable,
        ignore_recipe_esmvaltool_options=sentinel.ignore_recipe_esmvaltool_options,
        ignore_recipe_srun_options=sentinel.ignore_recipe_srun_options,
        additional_esmvaltool_options=sentinel.additional_esmvaltool_options,
        additional_srun_options=sentinel.additional_srun_options,
        output_dir_slurm=sentinel.output_dir_slurm,
    )


def test___init__(sentinel_job: Job) -> None:
    assert sentinel_job._recipe == sentinel.recipe
    assert sentinel_job._esmvaltool_config == sentinel.esmvaltool_config
    assert sentinel_job._account == sentinel.account
    assert sentinel_job._esmvaltool_executable == sentinel.esmvaltool_executable
    assert sentinel_job._srun_executable == sentinel.srun_executable
    assert (
        sentinel_job._ignore_recipe_esmvaltool_options
        == sentinel.ignore_recipe_esmvaltool_options
    )
    assert (
        sentinel_job._ignore_recipe_srun_options == sentinel.ignore_recipe_srun_options
    )
    assert (
        sentinel_job._additional_esmvaltool_options
        == sentinel.additional_esmvaltool_options
    )
    assert sentinel_job._additional_srun_options == sentinel.additional_srun_options
    assert sentinel_job._output_dir_slurm == sentinel.output_dir_slurm


def test___repr__(sentinel_job: Job) -> None:
    assert (
        repr(sentinel_job)
        == "Job(sentinel.recipe, esmvaltool_config=sentinel.esmvaltool_config, "
        "account=sentinel.account)"
    )


def test_output_dir(sentinel_job: Job, tmp_path: Path) -> None:
    esmvaltool_output_dir = tmp_path / "esmvaltool_output"
    esmvaltool_output_dir.mkdir(parents=True, exist_ok=True)
    recipe_output_dir = esmvaltool_output_dir / "recipe_test_20000101_000000"
    recipe_output_dir.mkdir(parents=True, exist_ok=True)
    recipe = Recipe(
        tmp_path / "recipe_test.yml",
        sentinel.recipe_test_template,
        [],
        "*",
    )
    esmvaltool_config = ESMValToolConfig(
        tmp_path / "esmvaltool_config.yml",
        sentinel.esmvaltool_config_templates,
        [],
        esmvaltool_output_dir,
        {},
    )
    sentinel_job._recipe = recipe
    sentinel_job._esmvaltool_config = esmvaltool_config

    assert sentinel_job.output_dir == recipe_output_dir


@pytest.mark.parametrize(
    ("poll_return_value", "is_finished"),
    [
        (None, False),
        (0, True),
        (1, True),
    ],
)
def test_is_finished(
    poll_return_value: int | None,
    is_finished: bool,
    sentinel_job: Job,
    mocker: pytest_mock.MockerFixture,
) -> None:
    mocked_popen = mocker.Mock(spec_set=subprocess.Popen)
    mocked_popen.poll.return_value = poll_return_value
    sentinel_job._process = mocked_popen
    assert sentinel_job.is_finished() == is_finished


@pytest.mark.parametrize(
    ("poll_return_value", "status"),
    [
        (None, "is running"),
        (0, "finished successfully"),
        (1, "failed with code 1"),
    ],
)
def test_log_status(
    poll_return_value: int | None,
    status: str,
    sentinel_job: Job,
    mocker: pytest_mock.MockerFixture,
) -> None:
    mocked_popen = mocker.Mock(spec=subprocess.Popen)
    mocked_popen.poll.return_value = poll_return_value
    mocked_popen.returncode = poll_return_value
    sentinel_job._process = mocked_popen
    assert status in sentinel_job.log_status()
