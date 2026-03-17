from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import iconeval._io_handler
from iconeval._io_handler import IconEvalIOHandler

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def input_dirs(tmp_path: Path) -> list[Path]:
    input_dirs = [
        tmp_path / "input_1",
        tmp_path / "input_2",
    ]
    for input_dir in input_dirs:
        input_dir.mkdir(parents=True, exist_ok=True)
    return input_dirs


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def test___repr__(input_dirs: list[Path], output_dir: Path) -> None:
    io_handler = IconEvalIOHandler(input_dirs, output_dir, "my_run_name")
    expected_output_dir = output_dir / "my_run_name_20000101_000000UTC"
    assert repr(io_handler) == (
        f"IconEvalIOHandler(input_dirs={input_dirs!r}, output_dir="
        f"{expected_output_dir!r}, run_name='my_run_name')"
    )


def test_input_dirs(input_dirs: list[Path], output_dir: Path) -> None:
    io_handler = IconEvalIOHandler(input_dirs, output_dir, "my_run_name")
    assert io_handler.input_dirs == input_dirs


def test_no_output_dir(
    input_dirs: list[Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(iconeval._io_handler.Path, "cwd", lambda: tmp_path)
    io_handler = IconEvalIOHandler(input_dirs, None, None)
    assert (
        io_handler.output_dir
        == tmp_path / "output_iconeval" / "input_1_input_2_20000101_000000UTC"
    )
    assert io_handler.run_name == "input_1_input_2"
