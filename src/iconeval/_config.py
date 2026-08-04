"""Manage ESMValTool configurations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import ESMValToolConfigTemplate


@dataclass(frozen=True, kw_only=True)
class ESMValToolConfig:
    """Manage ESMValTool configuration."""

    path: Path
    template: ESMValToolConfigTemplate = field(repr=False)
    simulations_info: list[SimulationInfo] = field(repr=False)
    output_dir: Path = field(repr=False)
    dask_config: dict[str, Any] = field(repr=False)

    @property
    def dir(self) -> Path:
        """Configuration directory."""
        return self.path.parent
