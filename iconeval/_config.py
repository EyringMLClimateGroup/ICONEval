"""Module that manages ESMValTool configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._simulation_info import SimulationInfo
    from iconeval._templates import ESMValToolConfigTemplate


@dataclass(frozen=True)
class ESMValToolConfig:
    """Represents an ESMValTool configuration file."""

    path: Path = field(kw_only=True)
    template: ESMValToolConfigTemplate = field(repr=False, kw_only=True)
    simulations_info: list[SimulationInfo] = field(repr=False, kw_only=True)
    output_dir: Path = field(repr=False, kw_only=True)
    dask_config: dict[str, Any] = field(repr=False, kw_only=True)

    @property
    def dir(self) -> Path:
        """Configuration directory."""
        return self.path.parent
