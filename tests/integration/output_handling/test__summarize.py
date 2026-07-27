from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from iconeval.output_handling._summarize import summarize

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_datadir.plugin import LazyDataDir

    from tests.integration import OutputDirRegression


def run_summarize_regression_test(
    esmvaltool_output: Path,
    expected_output_dir: Path,
    output_dir_regression: OutputDirRegression,
    **kwargs: Any,
) -> None:
    original_dir_contents = [obj.name for obj in esmvaltool_output.iterdir()]
    summarize(esmvaltool_output, **kwargs)
    output_dir_regression.check(
        esmvaltool_output,
        expected_output_dir,
        ignore_top_level_files_and_dirs=original_dir_contents,
    )


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
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    expected_output_dir: Path,
) -> None:
    run_summarize_regression_test(
        lazy_shared_datadir / "recipes_zonal-means",
        expected_output_dir / expected_output_name,
        output_dir_regression,
        description=description,
    )


def test_summarize_empty_logs(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    expected_output_dir: Path,
) -> None:
    run_summarize_regression_test(
        lazy_shared_datadir / "recipes_maps",
        expected_output_dir / "test_summarize_empty_logs",
        output_dir_regression,
    )


def test_summarize_no_debug_log(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    expected_output_dir: Path,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.unlink()
    run_summarize_regression_test(
        esmvaltool_output,
        expected_output_dir / "test_summarize_no_debug_log",
        output_dir_regression,
    )


def test_summarize_debug_log_single_line(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
    expected_output_dir: Path,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.write_text("this is a single line that cannot be used to infer runtime")
    run_summarize_regression_test(
        esmvaltool_output,
        expected_output_dir / "test_summarize_debug_log_single_line",
        output_dir_regression,
    )
