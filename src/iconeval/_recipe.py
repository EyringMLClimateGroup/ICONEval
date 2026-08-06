"""Manage ESMValTool recipes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import RecipeTemplate
    from iconeval._typing import FacetType


@dataclass(frozen=True, kw_only=True)
class Recipe:
    """Manage ESMValTool recipe."""

    path: Path
    template: RecipeTemplate = field(repr=False)
    simulations_info: list[SimulationInfo] = field(repr=False)
    timerange: FacetType = field(repr=False)

    @property
    def name(self) -> str:
        """Name of recipe."""
        return self.path.stem
