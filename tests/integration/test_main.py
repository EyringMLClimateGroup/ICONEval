from __future__ import annotations

from typing import TYPE_CHECKING

from iconeval.main import icon_evaluation
from tests.integration import assert_output

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import Mock


def test_icon_evaluation_single_input(
    expected_output_dir: Path,
    tmp_path: Path,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_dir = icon_evaluation(input_dir, output_dir=output_dir)

    # pdfs and slurm dirs are empty. Empty directories cannot be checked in on
    # git, so we remove them here.
    empty_dirs = ["pdfs", "slurm"]
    for empty_dir in empty_dirs:
        empty_path = output_dir / empty_dir
        assert empty_path.is_dir()
        assert len(list(empty_path.iterdir())) == 0
        empty_path.rmdir()

    # Check non-empty dirs
    expected_output = expected_output_dir / "test_icon_evaluation_single_input"
    assert_output([input_dir], output_dir, expected_output)
