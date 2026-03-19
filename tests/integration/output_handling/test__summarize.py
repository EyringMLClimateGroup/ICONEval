from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from iconeval.output_handling._summarize import summarize
from tests.integration import assert_output

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("description", "expected_output_name"),
    [
        (None, "test_summarize_without_description"),
        ("very short description", "test_summarize_with_description"),
    ],
)
def test_summarize(
    description: str | None,
    expected_output_name: str,
    expected_output_dir: Path,
    sample_data_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Copy sample output to temporary directory so files can be created
    src_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    esmvaltool_output = tmp_path / "recipes_zonal-means"
    esmvaltool_output.mkdir(parents=True, exist_ok=True)
    subdirs = [
        "recipe_basics_zonal_mean_lines_20260318_093429",
        "recipe_ocean_zonal_mean_lines_20260318_093429",
    ]
    for subdir in subdirs:
        shutil.copytree(src_dir / subdir, esmvaltool_output / subdir)

    summarize(esmvaltool_output, description=description)

    # Check output; for this, we remove the previously created subdirectories
    for subdir in subdirs:
        shutil.rmtree(esmvaltool_output / subdir)
    assert_output(
        [],
        esmvaltool_output,
        expected_output_dir / expected_output_name,
    )
