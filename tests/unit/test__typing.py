from __future__ import annotations

from pathlib import Path
from typing import Literal

from iconeval._typing import FacetType, OptionValueType, RealmType


def test_facet_type() -> None:
    assert FacetType.__value__ == bool | str | Path | int | float | list | dict | None


def test_option_value_type() -> None:
    assert OptionValueType.__value__ == str | int | float


def test_realm_type() -> None:
    assert (
        RealmType.__value__
        == Literal[
            "all",
            "atmosphere",
            "ocean",
            "land",
            "sanity-consistency-checks",
        ]
    )
