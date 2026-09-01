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
    name: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Initialize class instance."""
        # See https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(self, "name", self.path.stem)
