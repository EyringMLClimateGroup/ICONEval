from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from iconeval.output_handling._summarize import summarize
from tests.integration import assert_output, copy_to_tmp_path

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
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    tmp_path: Path,
) -> None:
    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        summarize(esmvaltool_output, description=description)
    assert_output(
        tmp_path,
        esmvaltool_output,
        expected_output_dir / expected_output_name,
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )


def test_summarize_empty_output(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    tmp_path: Path,
) -> None:
    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_maps"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        summarize(esmvaltool_output)
    assert_output(
        tmp_path,
        esmvaltool_output,
        expected_output_dir / "test_summarize_empty_logs",
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )
