"""Module that manages ESMValTool recipes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import RecipeTemplate
    from iconeval._typing import FacetType


@dataclass(frozen=True)
class Recipe:
    """Class representing an ESMValTool recipe."""

    path: Path
    template: RecipeTemplate
    simulations_info: list[SimulationInfo]
    timerange: FacetType

    @property
    def name(self) -> str:
        """Name of recipe."""
        return self.path.stem
