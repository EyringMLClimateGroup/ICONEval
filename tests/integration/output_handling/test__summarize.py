from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from iconeval._session import Session
from iconeval._simulation_info import SimulationInfo
from iconeval.output_handling._summarize import get_html_description, summarize
from tests.integration import assert_output, copy_to_tmp_path

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def simulations_info() -> list[SimulationInfo]:
    simulation_info_1 = SimulationInfo(
        date="2000-01-01 00:00:00",
        exp="exp_1",
        grid_info="R2B5",
        guessed_facets={"dataset": "ICON", "project": "ICON"},
        namelist_files=[Path("namelist_1"), Path("namelist_2")],
        owner="OWNER 1",
        path=Path("/path/to/exp_1"),
    )
    simulation_info_2 = SimulationInfo(
        date="2000-01-01 00:00:00",
        exp="exp_2",
        grid_info="unknown",
        guessed_facets={},
        namelist_files=[],
        owner="OWNER 2",
        path=Path("/path/to/exp_2"),
    )
    return [simulation_info_1, simulation_info_2]


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


def test_summarize_with_detailed_description(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    simulations_info: list[SimulationInfo],
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    mocked_session = mocker.Mock(spec_set=Session, simulations_info=simulations_info)
    description = get_html_description(mocked_session, datetime(2001, 1, 1))
    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-mean_maps"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        summarize(esmvaltool_output, description=description)
    assert_output(
        tmp_path,
        esmvaltool_output,
        expected_output_dir / "test_summarize_with_detailed_description",
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )
