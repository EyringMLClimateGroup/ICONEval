"""Module that manages ESMValTool configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import ESMValToolConfigTemplate


@dataclass(frozen=True)
class ESMValToolConfig:
    """Represents an ESMValTool configuration file."""

    path: Path
    template: ESMValToolConfigTemplate
    simulations_info: list[SimulationInfo]
    output_dir: Path
    dask_config: dict[str, Any]

    @property
    def dir(self) -> Path:
        """Configuration directory."""
        return self.path.parent
