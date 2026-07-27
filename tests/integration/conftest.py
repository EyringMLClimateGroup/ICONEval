from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration import OutputDirRegression

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def output_dir_regression(
    original_datadir: Path,
    request: pytest.FixtureRequest,
) -> OutputDirRegression:
    return OutputDirRegression(original_datadir, request)


@pytest.fixture
def tmp_input_dir(tmp_path: Path) -> Path:
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    return input_dir


@pytest.fixture
def tmp_input_dirs(tmp_path: Path) -> list[Path]:
    input_dirs = [tmp_path / "input_1", tmp_path / "input_2"]
    for input_dir in input_dirs:
        input_dir.mkdir(parents=True, exist_ok=True)
    return input_dirs


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
