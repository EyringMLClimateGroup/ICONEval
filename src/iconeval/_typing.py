"""Manage ICONEval types."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

type FacetType = bool | str | Path | int | float | list | dict | None

type OptionValueType = str | int | float

type RealmType = Literal[
    "all",
    "atmosphere",
    "ocean",
    "land",
    "sanity-consistency-checks",
]
