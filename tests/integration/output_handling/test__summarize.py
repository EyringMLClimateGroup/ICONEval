from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from iconeval.output_handling._summarize import summarize

if TYPE_CHECKING:

    from pytest_datadir.plugin import LazyDataDir

    from tests.integration import OutputDirRegression


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
    esmvaltool_output = lazy_shared_datadir / "recipes_zonal-means"
    summarize(esmvaltool_output, description=description)
    output_dir_regression.check(esmvaltool_output)


def test_summarize_empty_logs(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    summarize(esmvaltool_output)
    output_dir_regression.check(esmvaltool_output)


def test_summarize_no_debug_log(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.unlink()
    summarize(esmvaltool_output)
    output_dir_regression.check(esmvaltool_output)


def test_summarize_debug_log_single_line(
    output_dir_regression: OutputDirRegression,
    lazy_shared_datadir: LazyDataDir,
) -> None:
    esmvaltool_output = lazy_shared_datadir / "recipes_maps"
    debug_log = esmvaltool_output / "recipe_basics_maps" / "run" / "main_log_debug.txt"
    debug_log.write_text("this is a single line that cannot be used to infer runtime")
    summarize(esmvaltool_output)
    output_dir_regression.check(esmvaltool_output)
