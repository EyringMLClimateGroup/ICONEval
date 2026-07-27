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
    output_dir_regression: OutputDirRegression,
    **kwargs: Any,
) -> None:
    summarize(esmvaltool_output, **kwargs)
    output_dir_regression.check(esmvaltool_output)


@pytest.mark.parametrize(
    "description",
    [
        pytest.param(None, id="without_description"),
        pytest.param("very short description", id="with_description"),
    ],
)
def test_summarize(
    description: str | None,
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    run_summarize_regression_test(
        lazy_shared_datadir / "recipes_zonal-means",
        output_dir_regression,
        description=description,
    )


def test_summarize_empty_logs(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    run_summarize_regression_test(
        lazy_shared_datadir / "recipes_maps",
        output_dir_regression,
    )


def test_summarize_no_debug_log(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.unlink()
    run_summarize_regression_test(esmvaltool_output, output_dir_regression)


def test_summarize_debug_log_single_line(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.write_text("this is a single line that cannot be used to infer runtime")
    run_summarize_regression_test(esmvaltool_output, output_dir_regression)
