"""Module that manages ESMValTool recipes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import RecipeTemplate
    from iconeval._typing import FacetType


@dataclass(frozen=True)
class Recipe:
    """Class representing an ESMValTool recipe."""

    path: Path = field(kw_only=True)
    template: RecipeTemplate = field(repr=False, kw_only=True)
    simulations_info: list[SimulationInfo] = field(repr=False, kw_only=True)
    timerange: FacetType = field(repr=False, kw_only=True)

    @property
    def name(self) -> str:
        """Name of recipe."""
        return self.path.stem
