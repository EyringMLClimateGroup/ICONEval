"""Generate tag table from given recipe templates.

Simply run with

```bash
python doc/generate_tag_table.py
```

"""  # noqa: INP001

from collections import defaultdict
from pathlib import Path
from textwrap import dedent

from py_markdown_table.markdown_table import markdown_table

from iconeval._io_handler import IconEvalIOHandler
from iconeval._templates import RecipeTemplate

HEADER: str = dedent(
    """\
    [Back to README](../README.md)

    # Available Tags

    """,
)
TAGS_FILE: Path = Path(__file__).parent / "tags.md"


def main() -> None:
    """Generate tag table from given recipe templates."""
    recipe_template_paths = IconEvalIOHandler.DEFAULT_RECIPE_TEMPLATE_DIR.rglob("*.yml")
    tags: dict[str, list[str]] = defaultdict(list)
    for recipe_template_path in recipe_template_paths:
        recipe_template = RecipeTemplate(recipe_template_path)
        for tag in recipe_template.tags:
            tags[tag].append(
                f"[{recipe_template.name}](https://github.com/"
                f"EyringMLClimateGroup/ICONEval/blob/main/iconeval/"
                f"recipe_templates/{recipe_template.path.name})",
            )
    tags = dict(sorted(tags.items()))
    print("Found tags:")
    for tag in tags:
        print(f"- {tag}")
    print()

    table: list[dict[str, str]] = [
        {"Tag": f"`{tag}`", "Recipes": ", ".join(recipes)}
        for tag, recipes in tags.items()
    ]
    markdown_options = {
        "quote": False,
        "row_sep": "markdown",
    }
    table_str = markdown_table(table).set_params(**markdown_options).get_markdown()

    file_contents = HEADER + table_str
    TAGS_FILE.write_text(file_contents, encoding="utf-8")
    print(f"Wrote {TAGS_FILE}")


if __name__ == "__main__":
    main()
