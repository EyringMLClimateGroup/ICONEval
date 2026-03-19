"""Generate tag table from given recipe templates.

Simply run with

```bash
python doc/generate_tag_table.py
```

"""  # noqa: INP001

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from py_markdown_table.markdown_table import markdown_table

from iconeval._io_handler import IconEvalIOHandler
from iconeval._templates import map_tags_to_recipes

if TYPE_CHECKING:
    from iconeval._templates import RecipeTemplate

HEADER: str = dedent(
    """\
    [Back to README](../README.md)

    # Available Tags

    """,
)
TAGS_FILE: Path = Path(__file__).parent / "tags.md"


def _get_link(recipe_template: RecipeTemplate) -> str:
    """Get link to recipe template."""
    return (
        f"[{recipe_template.name}](https://github.com/EyringMLClimateGroup/ICONEval/"
        f"blob/main/iconeval/recipe_templates/{recipe_template.path.name})"
    )


def main() -> None:
    """Generate tag table from given recipe templates."""
    all_recipe_templates = IconEvalIOHandler.DEFAULT_RECIPE_TEMPLATE_DIR.rglob("*.yml")
    tag_map: dict[str, list[str]] = {
        tag: [_get_link(r) for r in recipe_templates]
        for tag, recipe_templates in map_tags_to_recipes(all_recipe_templates).items()
    }
    tag_map = dict(sorted(tag_map.items()))
    print("Found tags:")  # noqa: T201
    for tag in tag_map:
        print(f"- {tag}")  # noqa: T201
    print()  # noqa: T201

    table: list[dict[str, str]] = [
        {"Tag": f"`{tag}`", "Recipes": ", ".join(recipes)}
        for tag, recipes in tag_map.items()
    ]
    markdown_options = {
        "quote": False,
        "row_sep": "markdown",
    }
    table_str = markdown_table(table).set_params(**markdown_options).get_markdown()

    file_contents = HEADER + table_str
    TAGS_FILE.write_text(file_contents, encoding="utf-8")
    print(f"Wrote {TAGS_FILE}")  # noqa: T201


if __name__ == "__main__":
    main()
