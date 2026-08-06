from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from iconeval._simulation_info import SimulationInfo

if TYPE_CHECKING:
    from pytest_datadir.plugin import LazyDataDir


@pytest.mark.parametrize(
    ("exp", "grid_info", "dataset", "project", "namelist_files"),
    [
        (
            "icon_example_run",
            "R02B05",
            "ICON",
            "ICON",
            ["NAMELIST_ICON_output_atm"],
        ),
        (
            "icon-xpp_example_run",
            "R02B05",
            "ICON-XPP",
            "ICON",
            ["NAMELIST_ICON_output_atm"],
        ),
        (
            "icon-no-grid_example_run",
            "unknown",
            "ICON",
            "ICON",
            [],
        ),
    ],
)
def test_from_path(
    exp: str,
    grid_info: str,
    dataset: str,
    project: str,
    namelist_files: list[str | Path],
    lazy_datadir: LazyDataDir,
) -> None:
    simulation_output = lazy_datadir / exp
    namelist_files = [simulation_output / n for n in namelist_files]

    simulation_info = SimulationInfo.from_path(simulation_output)

    assert simulation_info.date == "2000-01-01 00:00:00"
    assert simulation_info.exp == exp
    assert simulation_info.grid_info == grid_info
    assert simulation_info.guessed_facets == {
        "dataset": dataset,
        "exp": exp,
        "project": project,
    }
    assert simulation_info.namelist_files == namelist_files
    assert simulation_info.owner == "ICONEval User"
    assert simulation_info.path == simulation_output


@pytest.mark.parametrize(
    ("exp", "dataset"),
    [
        ("icon_example_run", "ICON"),
        ("icon-xpp_example_run", "ICON-XPP"),
    ],
)
def test__guess_dataset(exp: str, dataset: str, lazy_datadir: LazyDataDir) -> None:
    simulation_output = lazy_datadir / exp
    assert SimulationInfo._guess_dataset(simulation_output) == dataset


def test_icon__guess_project() -> None:
    path = Path("/path/to/simulation")
    assert SimulationInfo._guess_project(path) == "ICON"
