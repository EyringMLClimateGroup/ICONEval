from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from iconeval.output_handling._summarize import summarize
from tests.integration import assert_output, copy_to_tmp_path

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("description", "sample_name", "expected_output_name"),
    [
        (
            None,
            "recipes_zonal-mean",
            "test_summarize_recipes_zonal-mean_no_description",
        ),
        (
            "description",
            "recipes_zonal-mean",
            "test_summarize_recipes_zonal-mean_description",
        ),
        (None, "recipes_map", "test_summarize_recipes_map"),
        (None, "recipes_zonal-mean_maps", "test_summarize_recipes_zonal-mean_maps"),
    ],
)
def test_summarize(
    description: str | None,
    sample_name: str,
    expected_output_name: str,
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    tmp_path: Path,
) -> None:
    sample_dir = sample_data_path / "esmvaltool_output" / sample_name
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        summarize(esmvaltool_output, description=description)
    assert_output(
        tmp_path,
        esmvaltool_output,
        expected_output_dir / expected_output_name,
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )
