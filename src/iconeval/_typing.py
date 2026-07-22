"""Manage ICONEval types."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

FacetType = None | bool | str | Path | int | float | list | dict

OptionValueType = str | int | float

RealmType = Literal[
    "all",
    "atmosphere",
    "ocean",
    "land",
    "sanity-consistency-checks",
]
