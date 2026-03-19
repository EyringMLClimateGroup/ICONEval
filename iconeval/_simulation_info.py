"""Module that manages ESMValTool recipes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from iconeval import get_user_name

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._typing import FacetType


@dataclass(frozen=True)
class SimulationInfo:
    date: str = field(repr=False, kw_only=True)
    exp: str = field(repr=False, kw_only=True)
    grid_info: str = field(repr=False, kw_only=True)
    guessed_facets: dict[str, FacetType] = field(repr=False, kw_only=True)
    namelist_files: list[Path] = field(repr=False, kw_only=True)
    owner: str = field(repr=False, kw_only=True)
    path: Path = field(kw_only=True)

    @classmethod
    def from_path(cls, path: Path) -> SimulationInfo:
        """Load simulation info from simulation path."""
        dir_stat = path.stat()

        # Date and time
        date = datetime.fromtimestamp(dir_stat.st_ctime, tz=UTC).strftime(
            "%Y-%m-%d %H:%M:%S%z",
        )

        # Experiment name
        exp = path.name

        # Grid information (e.g., R02B04, R02B05)
        grid_pattern = re.compile(r"R\d{2}B\d{2}")
        grid_info = "unknown"
        for grid_file in path.glob("icon_grid_*"):
            match = grid_pattern.search(grid_file.name)
            if match:
                grid_info = match.group(0)
                break

        # Guessed facets
        guessed_facets: dict[str, FacetType] = {
            "dataset": cls._guess_dataset(path),
            "exp": exp,
            "project": cls._guess_project(path),
        }

        # Namelist files
        namelist_files = list(path.glob("NAMELIST_*"))

        # Owner
        owner = get_user_name(dir_stat.st_uid)

        return cls(
            date=date,
            exp=exp,
            grid_info=grid_info,
            guessed_facets=guessed_facets,
            namelist_files=namelist_files,
            owner=owner,
            path=path,
        )

    @staticmethod
    def _guess_dataset(path: Path) -> str:
        """Guess dataset facet."""
        # ICON-XPP
        namelist = path / "NAMELIST_ICON_output_atm"
        if namelist.is_file():
            namelist_content = namelist.read_text()
            if "ECHAM_" not in namelist_content:
                return "ICON-XPP"

        # Default
        return "ICON"

    @staticmethod
    def _guess_project(path: Path) -> str:  # noqa: ARG004
        """Guess project facet."""
        return "ICON"
