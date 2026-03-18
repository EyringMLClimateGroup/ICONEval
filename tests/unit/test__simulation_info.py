from __future__ import annotations

from pathlib import Path

import pytest

from iconeval._simulation_info import SimulationInfo


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
    sample_data_path: Path,
) -> None:
    sample_data = sample_data_path / "icon_output" / exp
    namelist_files = [sample_data / n for n in namelist_files]

    simulation_info = SimulationInfo.from_path(sample_data)

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
    assert simulation_info.path == sample_data


@pytest.mark.parametrize(
    ("exp", "dataset"),
    [
        ("icon_example_run", "ICON"),
        ("icon-xpp_example_run", "ICON-XPP"),
    ],
)
def test__guess_dataset(exp: str, dataset: str, sample_data_path: Path) -> None:
    path = sample_data_path / "icon_output" / exp
    assert SimulationInfo._guess_dataset(path) == dataset


def test_icon__guess_project() -> None:
    path = Path("/path/to/simulation")
    assert SimulationInfo._guess_project(path) == "ICON"
