from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from iconeval._dependencies import (
    latex_is_available,
    verify_esmvaltool_installation,
    verify_slurm_installation,
)

if TYPE_CHECKING:
    from unittest.mock import Mock


def test_latex_is_available_true(mocked_subprocess__dependencies: Mock) -> None:
    assert latex_is_available() is True


def test_latex_is_available_false(mocked_subprocess__dependencies: Mock) -> None:
    mocked_subprocess__dependencies.run.return_value.returncode = 1
    assert latex_is_available() is False


def test_verify_esmvaltool_installation_success(
    mocked_subprocess__dependencies: Mock,
) -> None:
    verify_esmvaltool_installation("esmvaltool")


def test_verify_esmvaltool_installation_fail(
    mocked_subprocess__dependencies: Mock,
) -> None:
    mocked_subprocess__dependencies.run.return_value.returncode = 1
    msg = r"esmvaltool command not found"
    with pytest.raises(RuntimeError, match=msg):
        verify_esmvaltool_installation("esmvaltool")


def test_verify_slurm_installation_success(
    mocked_subprocess__dependencies: Mock,
) -> None:
    verify_slurm_installation("srun")


def test_verify_slurm_installation_fail(
    mocked_subprocess__dependencies: Mock,
) -> None:
    mocked_subprocess__dependencies.run.return_value.returncode = 1
    msg = r"srun command not found"
    with pytest.raises(RuntimeError, match=msg):
        verify_slurm_installation("srun")
