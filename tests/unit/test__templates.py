from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from iconeval._templates import ESMValToolConfigTemplate, RecipeTemplate, Template

if TYPE_CHECKING:
    from iconeval._typing import FacetType


@pytest.fixture
def template_path(tmp_path: Path) -> Path:
    file = tmp_path / "template"
    file.touch()
    return file


@pytest.fixture
def esmvaltool_config_template_path(tmp_path: Path) -> Path:
    file = tmp_path / "esmvaltool_config_template"
    file.touch()
    return file


@pytest.fixture
def recipe_template_path(tmp_path: Path) -> Path:
    file = tmp_path / "recipe_template"
    file.touch()
    return file


def test_template___repr__(template_path: Path) -> None:
    assert (
        repr(Template(template_path, check_placeholders=False))
        == f"Template(path={template_path!r})"
    )


def test_template__check_placeholders(template_path: Path) -> None:
    Template(template_path)


def test_template__fill_placeholders(template_path: Path) -> None:
    template_dict = {
        "d": "{{replace_with_dict}}",
        "l": "{{replace_with_list}}",
        "p": "{{replace_with_path}}",
    }
    placeholders: dict[str, FacetType] = {
        "{{replace_with_dict}}": {
            "a": "a",
            "b": Path("b"),
            Path("c"): "c",
            Path("d"): Path("d"),
        },
        "{{replace_with_list}}": ["a", Path("b")],
        "{{replace_with_path}}": Path("a"),
    }
    filled_dict = Template(template_path)._fill_placeholders(
        template_dict,
        placeholders,
    )
    assert filled_dict == {
        "d": {"a": "a", "b": "b", "c": "c", "d": "d"},
        "l": ["a", "b"],
        "p": "a",
    }


def test_esmvaltool_config_template___repr__(
    esmvaltool_config_template_path: Path,
) -> None:
    assert (
        repr(
            ESMValToolConfigTemplate(
                esmvaltool_config_template_path,
                check_placeholders=False,
            ),
        )
        == f"ESMValToolConfigTemplate(path={esmvaltool_config_template_path!r})"
    )


def test_esmvaltool_config_template__check_placeholders(
    esmvaltool_config_template_path: Path,
) -> None:
    ESMValToolConfigTemplate(esmvaltool_config_template_path)


def test_recipe_template___repr__(recipe_template_path: Path) -> None:
    assert (
        repr(RecipeTemplate(recipe_template_path, check_placeholders=False))
        == f"RecipeTemplate(path={recipe_template_path!r})"
    )


def test_recipe_template__check_placeholders_fail(
    recipe_template_path: Path,
) -> None:
    msg = r"is not a valid recipe template, it needs to include '{{dataset_list}}'"
    with pytest.raises(ValueError, match=re.escape(msg)):
        RecipeTemplate(recipe_template_path)


@pytest.mark.parametrize(
    "option",
    [
        "#OPTION",
        "#OPTION --custom_option",
        "#OPTION --custom_option=1=2",
        "#OPTION invalid_option=1",
    ],
)
def test_recipe_template__parse_additional_options_fail(
    option: str,
    recipe_template_path: Path,
) -> None:
    recipe_template_path.write_text(option)
    template = RecipeTemplate(recipe_template_path, check_placeholders=False)
    msg = r"Invalid option option given in recipe template"
    with pytest.raises(ValueError, match=re.escape(msg)):
        template._parse_additional_options("#OPTION")
