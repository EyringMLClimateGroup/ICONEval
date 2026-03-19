from __future__ import annotations

import re
from typing import TYPE_CHECKING
from unittest.mock import sentinel

import pytest

import iconeval._dependencies
from iconeval._dependencies import (
    verify_esmvaltool_installation,
    verify_slurm_installation,
)

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mocked_subprocess(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(iconeval._dependencies, "subprocess", autospec=True)


def test_verify_esmvaltool_installation_success(mocked_subprocess: Mock) -> None:
    esmvaltool_executable = sentinel.esmvaltool
    mocked_subprocess.run.return_value.returncode = 0
    verify_esmvaltool_installation(esmvaltool_executable)
    mocked_subprocess.run.assert_called_once_with(
        ["which", esmvaltool_executable],
        shell=False,
        check=False,
        capture_output=True,
    )


def test_verify_esmvaltool_installation_fail(mocked_subprocess: Mock) -> None:
    mocked_subprocess.run.return_value.returncode = 1
    esmvaltool_executable = sentinel.esmvaltool
    msg = r"esmvaltool command not found"
    with pytest.raises(RuntimeError, match=re.escape(msg)):
        verify_esmvaltool_installation(esmvaltool_executable)
    mocked_subprocess.run.assert_called_once_with(
        ["which", esmvaltool_executable],
        shell=False,
        check=False,
        capture_output=True,
    )


def test_verify_slurm_installation_success(mocked_subprocess: Mock) -> None:
    mocked_subprocess.run.return_value.returncode = 0
    srun_executable = sentinel.srun
    verify_slurm_installation(srun_executable)
    mocked_subprocess.run.assert_called_once_with(
        ["which", srun_executable],
        shell=False,
        check=False,
        capture_output=True,
    )


def test_verify_slurm_installation_fail(mocked_subprocess: Mock) -> None:
    mocked_subprocess.run.return_value.returncode = 1
    srun_executable = sentinel.srun
    msg = r"srun command not found"
    with pytest.raises(RuntimeError, match=re.escape(msg)):
        verify_slurm_installation(srun_executable)
    mocked_subprocess.run.assert_called_once_with(
        ["which", srun_executable],
        shell=False,
        check=False,
        capture_output=True,
    )
