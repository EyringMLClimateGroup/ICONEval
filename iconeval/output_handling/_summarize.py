"""Create summary HTML for ESMValTool runs.

Copied and modified version of
https://github.com/ESMValGroup/ESMValTool/blob/main/esmvaltool/utils/testing/regression/summarize.py.

ESMValTool is licensed under a Apache License 2.0. A copy of this license is
available at https://github.com/ESMValGroup/ESMValTool/blob/main/LICENSE.

"""

from __future__ import annotations

import re
import textwrap
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from loguru import logger

from iconeval import get_user_name
from iconeval._templates import RecipeTemplate

if TYPE_CHECKING:
    from collections.abc import Iterable

    from iconeval._io_handler import IconEvalIOHandler
    from iconeval._typing import RealmType


logger = logger.opt(colors=True)


def get_html_description(io_handler: IconEvalIOHandler, date: datetime) -> str:
    """Create description of simulation(s) for HTML."""
    # Simulation-specific information
    simulations_info = io_handler.simulations_info
    sim_str = ""
    for index, sim_info in enumerate(simulations_info):
        namelist_files_html = "".join(
            f"<li>{path}</li>" for path in sim_info.namelist_files
        )

        sim_str += (
            f"<div>\n"
            f"  <span style='cursor: pointer;' "
            f"onclick=\"toggleAccordion('accordion-{index}',"
            f" 'arrow-{index}')\">\n"
            f"    <span id='arrow-{index}' style='display: inline-block; "
            f"transition: transform 0.2s;'>▶</span> "
            f"{sim_info.exp}</span>\n"
            f"  <div id='accordion-{index}' style='display: none; "
            f"margin-left: 20px;'>\n"
            f"    <br><p>Path: {sim_info.path}</p>\n"
            f"    <p>Created by: {sim_info.owner}</p>\n"
            f"    <p>Simulation Date: {sim_info.date}</p>\n"
            f"    <p>Grid Info: {sim_info.grid_info}</p>\n"
            f"    <p>Namelist Files:</p>\n"
            f"    <ul>{namelist_files_html}</ul>\n"
            f"  </div>\n"
            f"</div>\n"
        )

    # General information
    current_user = get_user_name()
    contacts = "".join(
        [
            f"<li>{person}</li>"
            for person in [
                "Manuel Schlund (manuel.schlund@dlr.de)",
                "Veronika Eyring (veronika.eyring@dlr.de)",
            ]
        ],
    )
    return (
        f"<p><b>Simulations:</b></p>\n"
        f"{sim_str}"
        f"<br><div>\n"
        f"  <p><b>Evaluation Date:</b> "
        f"{date.strftime('%Y-%m-%d %H:%M:%S%z')}</p>\n"
        f"  <p><b>ICONEval User:</b> {current_user}</p>\n"
        f"  <p><b>ICONEval Contacts:</b></p>\n"
        f"  <ul>{contacts}</ul>\n"
        f"</div>\n"
        f"<script>\n"
        f"  function toggleAccordion(accordionId, arrowId) {{\n"
        f"    var element = document.getElementById(accordionId);\n"
        f"    var arrow = document.getElementById(arrowId);\n"
        f"    if (element.style.display === 'none') {{\n"
        f"      element.style.display = 'block';\n"
        f"      arrow.style.transform = 'rotate(90deg)';\n"
        f"    }} else {{\n"
        f"      element.style.display = 'none';\n"
        f"      arrow.style.transform = 'rotate(0deg)';\n"
        f"    }}\n"
        f"  }}\n"
        f"</script>\n"
    )


def summarize(
    esmvaltool_output_dir: Path,
    description: str | None = None,
) -> None:
    """Create summary HTML."""
    _write_debug_html(esmvaltool_output_dir)
    realms: list[RealmType] = [
        "all",
        "atmosphere",
        "ocean",
        "land",
        "sanity-consistency-checks",
    ]
    for realm in realms:
        _write_index_html(
            realm,
            esmvaltool_output_dir,
            description=description,
        )
    logger.info(
        f"Successfully created summary HTML "
        f"<cyan>{esmvaltool_output_dir / 'index.html'}</cyan>",
    )


def _div(txt: str, class_: str) -> str:
    """Format text as html div."""
    return f"<div class='{class_}'>{txt}</div>"


def _generate_overview(realm: RealmType, output_dir: Path) -> list[str]:
    """Generate the lines of text for the overview page."""
    all_recipes: dict[str, list] = {}
    recipes: dict[str, Path] = {}  # only most recent versions of recipes

    for recipe_dir in sorted(Path(output_dir).glob("recipe_*")):
        log = recipe_dir / "run" / "main_log.txt"
        success = "Run was successful\n" in log.read_text()
        if not success:
            continue
        name = _get_recipe_name(recipe_dir)
        if name not in all_recipes:
            all_recipes[name] = []
        all_recipes[name].append(recipe_dir)

    # Select most recent versions of recipes
    for name, recipe_dirs in all_recipes.items():
        recipes[name] = sorted(recipe_dirs, key=_get_recipe_date)[-1]

    logger.debug(
        f"Found {len(recipes)} recipe(s) while generating summary HTML",
    )
    lines = []
    for name, recipe_dir in recipes.items():
        recipe_file = recipe_dir / "run" / f"recipe_{name}.yml"
        tags = RecipeTemplate(recipe_file, check_placeholders=False).tags

        # Filter recipes by tags
        if realm != "all" and realm not in tags:
            continue

        title, description = _get_title_and_description(recipe_file)
        figure = _get_first_figure(recipe_dir)
        recipe_url = f"{recipe_dir.relative_to(output_dir)}/index.html"
        entry_txt = _div(
            _div(
                "\n".join(
                    [
                        (
                            f"<img src='{figure.relative_to(output_dir)}' "
                            "class='card-img-top'/>"
                            if figure
                            else ""
                        ),
                        _div(
                            "\n".join(
                                [
                                    f'<h5 class="card-title">{title}</h5>',
                                    f'<p class="card-text">{description} '
                                    f'<a href="{recipe_url}">'
                                    '<i class="bi bi-arrow-right-circle"></i>'
                                    "</a></p>",
                                ],
                            ),
                            "card-body",
                        ),
                    ],
                ),
                "card",
            ),
            "col",
        )
        lines.append(entry_txt)

    return lines


def _generate_summary(output_dir: Path) -> list[str]:
    """Generate the lines of text for the debug summary view."""
    lines = []

    column_titles = [
        "status",
        "recipe output",
        "run date",
        "estimated run duration",
        "estimated max memory (GB)",
        "average cpu",
    ]
    lines.append(_tr(_th(txt) for txt in column_titles))

    for recipe_dir in sorted(Path(output_dir).glob("recipe_*")):
        log = recipe_dir / "run" / "main_log.txt"
        success = "Run was successful\n" in log.read_text()
        if success:
            status = "success"
        else:
            debug_log = f"{recipe_dir.name}/run/main_log_debug.txt"
            status = "failed (" + _link(debug_log, "debug") + ")"
        name = f"recipe_{_get_recipe_name(recipe_dir)}"
        date = _get_recipe_date(recipe_dir)
        resource_usage = _get_resource_usage(recipe_dir)

        entry = []
        entry.append(status)
        entry.append(_link(f"{recipe_dir.name}/index.html", name))
        entry.append(date.strftime("%Y-%m-%d %H:%M:%S%z"))
        entry.extend(resource_usage)

        entry_txt = _tr(_td(txt) for txt in entry)
        lines.append(entry_txt)

    return lines


def _get_first_figure(recipe_dir: Path) -> Path | None:
    """Get the first figure."""
    plot_dir = recipe_dir / "plots"
    figures = plot_dir.glob("**/*.png")
    try:
        return next(figures)
    except StopIteration:
        return None


def _get_index_html_name(realm: RealmType) -> str:
    """Get name of index file."""
    if realm == "all":
        return "index.html"
    return f"index_{realm}.html"


def _get_nice_realm_name(realm: RealmType) -> str:
    """Get nice realm name."""
    if realm == "sanity-consistency-checks":
        return "Sanity/Consistency"
    return realm.capitalize()


def _get_recipe_date(recipe_dir: Path) -> datetime:
    """Extract recipe date from output dir."""
    date_pattern = r"(?P<datetime>[0-9]{8}_[0-9]{6})-?[0-9]*$"
    regex = re.search(date_pattern, recipe_dir.stem)
    if regex is not None:
        date_str = regex.group("datetime")
        return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
    return datetime.now()


def _get_recipe_name(recipe_dir: Path) -> str:
    """Extract recipe name from output dir."""
    # Only directories starting with "recipe_" are considered here, so the
    # following is safe
    recipe_str = recipe_dir.stem[7:]
    name_pattern = r"(?P<name>.*?)_[0-9]{8}_[0-9]{6}-?[0-9]*$"
    regex = re.match(name_pattern, recipe_str)
    if regex is not None:
        return regex.group("name")
    return recipe_str


def _get_resource_usage(recipe_dir: Path) -> list[str]:
    """Get recipe runtime (minutes), max memory (GB), avg CPU."""
    resource_usage = _read_resource_usage_file(recipe_dir)

    if not resource_usage or not resource_usage["Real time (s)"]:
        runtime = _get_runtime_from_debug(recipe_dir)
        runtime_str = "" if runtime is None else f"{runtime}"
        return [runtime_str, "", ""]

    runtime = resource_usage["Real time (s)"][-1]
    avg_cpu = resource_usage["CPU time (s)"][-1] / runtime * 100.0
    runtime = timedelta(seconds=round(runtime))
    memory = max(resource_usage["Memory (GB)"])

    return [f"{runtime}", f"{memory:.1f}", f"{avg_cpu:.1f}"]


def _get_runtime_from_debug(recipe_dir: Path) -> timedelta | None:
    """Try to read the runtime from the debug log."""
    debug_file = recipe_dir / "run" / "main_log_debug.txt"
    if not debug_file.exists():
        return None

    text = debug_file.read_text().strip()
    if not text:
        return None

    lines = text.split("\n")
    fmt = "%Y-%m-%d %H:%M:%S"
    end_date = None
    for line in lines[::-1]:
        try:
            end_date = datetime.strptime(line[:19], fmt)
        except ValueError:
            pass
        else:
            break
    if end_date is None:
        return None

    start_date = datetime.strptime(lines[0][:19], fmt)
    runtime = end_date - start_date
    return timedelta(seconds=round(runtime.total_seconds()))


def _get_title_and_description(recipe_file: Path) -> tuple[str, str]:
    """Get recipe title and description."""
    with recipe_file.open("rb") as file:
        recipe = yaml.safe_load(file)

    docs = recipe["documentation"]
    title = docs.get("title", recipe_file.stem.replace("_", " ").title())

    return title, docs["description"]


def _link(url: str, text: str) -> str:
    """Format text as html link."""
    return '<a href="' + url + '">' + text + "</a>"


def _read_resource_usage_file(recipe_dir: Path) -> dict:
    """Read resource usage from the log."""
    resource_file = recipe_dir / "run" / "resource_usage.txt"
    usage: dict[str, list] = {}

    if not resource_file.exists():
        return usage

    text = resource_file.read_text().strip()
    if not text:
        return usage

    lines = text.split("\n")
    for name in lines[0].split("\t"):
        usage[name] = []

    for line in lines[1:]:
        for key, value in zip(usage, line.split("\t"), strict=False):
            if key != "Date and time (UTC)":
                value = float(value)  # type: ignore[assignment]
            usage[key].append(value)

    return usage


def _td(txt: str) -> str:
    """Format text as html table data."""
    return "<td>" + txt + "</td>"


def _th(txt: str) -> str:
    """Format text as html table header."""
    return "<th>" + txt + "</th>"


def _tr(entries: Iterable[str]) -> str:
    """Format text entries as html table row."""
    return "<tr>" + "  ".join(entries) + "</tr>"


def _write_debug_html(output_dir: Path) -> None:
    """Write lines to debug.html."""
    header = textwrap.dedent(
        """
        <!doctype html>
        <html>
        <head>
            <title>ESMValTool recipes</title>
        </head>
        <style>
        #recipes {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }

        #recipes td, #recipes th {
            border: 1px solid #ddd;
            padding: 8px;
        }

        #recipes tr:nth-child(even){background-color: #f2f2f2;}

        #recipes tr:hover {background-color: #ddd;}

        #recipes th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: hsl(200, 50%, 50%);
            color: white;
        }
        </style>
        <body>
            <table id="recipes">
        """,
    )
    footer = textwrap.dedent(
        """
        </table>
        </body>
        </html>
        """,
    )
    lines = ["      " + line for line in _generate_summary(output_dir)]
    text = header + "\n".join(lines) + footer

    index_file = output_dir / "debug.html"
    index_file.write_text(text)
    logger.debug(f"Wrote file://{index_file.resolve()}")


def _write_index_html(
    realm: RealmType,
    output_dir: Path,
    description: str | None = None,
) -> None:
    """Write lines to index.html."""
    if description is None:
        description = ""

    def realm_button(realm_of_button: RealmType) -> str:
        """Create button to select realms."""
        background_color = "#1C1CC4" if realm == realm_of_button else "#222222"
        return textwrap.dedent(
            f"""\
            <div class="col-auto" style="width: 210px; margin: 10px;">
                <button
                    class="btn btn-primary btn-lg"
                    onclick="window.open('{_get_index_html_name(realm_of_button)}', '_self')"
                    style="margin: 10px; padding: 20px; background-color: {background_color}; width: 210px; border: none; box-shadow: none"
                    id="{realm_of_button}"
                >
                    {_get_nice_realm_name(realm_of_button)}
                </button>
            </div>
            """,  # noqa: E501
        )

    header = textwrap.dedent(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <title>ESMValTool results</title>
        </head>
        <body>
            <div class="container-fluid">
            <h1>
            <img src="https://github.com/ESMValGroup/ESMValTool/raw/main/doc/sphinx/source/figures/ESMValTool-logo-2.png" class="img-fluid">
            </h1>
            <p>
            {description}
            Missing something? Have a look at the <a href=debug.html>debug page</a>.
            <p>
            <input class="form-control searchbox-input" type="text" placeholder="Type something here to search...">
            <div class="row">
                {realm_button("all")}
                {realm_button("atmosphere")}
                {realm_button("land")}
                {realm_button("ocean")}
                {realm_button("sanity-consistency-checks")}
            </div>
            <br>
            <div class="row row-cols-1 row-cols-md-3 g-4">
        """,  # noqa: E501
    )
    footer = textwrap.dedent(
        """
        </div>
        </div>
        <script>
            $(document).ready(function(){
                $('.searchbox-input').on("keyup", function() {
                var value = $(this).val().toLowerCase();
                $(".col").filter(function() {
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                });
                });
            });
        </script>
        </body>
        </html>
        """,
    )

    lines = _generate_overview(realm, output_dir)
    if not lines:
        text = header + "\n" + "         <p><b>No results available.</b>" + footer
    else:
        lines = ["        " + line for line in lines]
        text = header + "\n".join(lines) + footer

    index_file = output_dir / _get_index_html_name(realm)
    index_file.write_text(text)
    logger.debug(f"Wrote file://{index_file.resolve()}")
