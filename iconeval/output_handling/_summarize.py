"""Create summary HTML for ESMValTool runs.

Copied and modified version of
https://github.com/ESMValGroup/ESMValTool/blob/main/esmvaltool/utils/testing/regression/summarize.py.

ESMValTool is licensed under a Apache License 2.0. A copy of this license is
available at https://github.com/ESMValGroup/ESMValTool/blob/main/LICENSE.

"""

from __future__ import annotations

import base64
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from loguru import logger

from iconeval import get_user_name
from iconeval._templates import RecipeTemplate
from iconeval.output_handling._templates_html import render_template

if TYPE_CHECKING:
    from collections.abc import Iterable

    from iconeval._session import Session
    from iconeval._typing import RealmType

# Maximum length of diagnostic caption displayed in card
CAPTION_MAX_LENGTH = 100


logger = logger.opt(colors=True)


def _read_diagnostic_provenance(diagnostic_dir: Path) -> dict:
    """Read diagnostic_provenance.yml and return as dict.

    Handles both standard YAML and YAML with anchors/aliases.
    """
    provenance_file = diagnostic_dir / "diagnostic_provenance.yml"
    if not provenance_file.exists():
        return {}

    try:
        with provenance_file.open() as f:
            # Use unsafe loader to handle YAML anchors/aliases
            data = yaml.unsafe_load(f)  # nosec
    except yaml.YAMLError:
        logger.warning(f"Could not parse {provenance_file}")
        return {}
    else:
        return data or {}


def _extract_all_diagnostics(output_dir: Path) -> list[DiagnosticInfo]:
    """Extract all diagnostics with their provenance data.

    PNGs are in plots/<diagnostic>/plot/*.png
    Provenance is in run/<diagnostic>/plot/diagnostic_provenance.yml

    Args:
        output_dir: The ESMValTool output directory

    Returns
    -------
        List of DiagnosticInfo objects for all diagnostics with PNG files
    """
    diagnostics = []

    for recipe_dir in sorted(Path(output_dir).glob("recipe_*")):
        # Check if recipe was successful
        log = recipe_dir / "run" / "main_log.txt"
        if not log.exists():
            continue
        success = "Run was successful\n" in log.read_text()
        if not success:
            continue

        recipe_name = _get_recipe_name(recipe_dir)
        recipe_date = _get_recipe_date(recipe_dir)

        # Get recipe tags for realm
        recipe_file = recipe_dir / "run" / f"recipe_{recipe_name}.yml"
        tags: set[str] = set()
        if recipe_file.exists():
            try:
                template = RecipeTemplate(
                    recipe_file,
                    check_placeholders=False,
                )
                tags = set(template.tags)
            except Exception:  # noqa: BLE001
                logger.debug("Could not load recipe template")

        # Determine realm from tags
        realm = "other"
        for tag in tags:
            if tag in ("atmosphere", "ocean", "land", "sanity-consistency-checks"):
                realm = tag
                break

        # Get recipe URL
        recipe_url = f"{recipe_dir.relative_to(output_dir)}/index.html"

        # Find all diagnostic directories with provenance in run/<diag>/plot
        for prov_dir in (recipe_dir / "run").glob("*/plot"):
            diag_name = prov_dir.parent.name
            provenance = _read_diagnostic_provenance(prov_dir)
            if not provenance:
                continue

            # Look for PNGs in plots/<diag_name>/plot/
            png_dir = recipe_dir / "plots" / diag_name / "plot"
            if not png_dir.exists():
                continue

            # Find all PNGs in this diagnostic's plot directory
            for png_file in sorted(png_dir.glob("*.png")):
                # Try to find matching provenance entry
                prov_data = None
                for key, value in provenance.items():
                    # Check if the PNG filename appears in the provenance key
                    if png_file.name in key:
                        prov_data = value
                        break

                # If no specific match, use first entry if only one
                if prov_data is None and len(provenance) == 1:
                    prov_data = next(iter(provenance.values()))

                if prov_data is None:
                    # Skip PNGs without provenance
                    continue

                # Extract relative path for HTML
                try:
                    relative_png = png_file.relative_to(output_dir)
                except ValueError:
                    # PNG is outside output_dir, skip
                    continue

                diagnostics.append(
                    DiagnosticInfo(
                        png_path=png_file,
                        relative_png_path=relative_png,
                        caption=prov_data.get("caption", ""),
                        authors=prov_data.get("authors", []),
                        plot_types=prov_data.get("plot_types", []),
                        long_names=prov_data.get("long_names", []),
                        ancestors=prov_data.get("ancestors", []),
                        recipe_name=recipe_name,
                        realm=realm,
                        recipe_date=recipe_date,
                        recipe_url=recipe_url,
                    ),
                )

    logger.debug(f"Found {len(diagnostics)} diagnostics with provenance")
    return diagnostics


def _get_filter_options(diagnostics: list[DiagnosticInfo]) -> FilterOptions:
    """Extract unique filter values from diagnostics."""
    options = FilterOptions()

    for diag in diagnostics:
        options.realms.add(diag.realm)
        options.plot_types.update(diag.plot_types)
        options.variables.update(diag.long_names)
        options.authors.update(diag.authors)

    return options


def _embed_image_as_base64(png_path: Path) -> str:
    """Embed PNG image as base64 data URL."""
    try:
        with png_path.open("rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
    except Exception:  # noqa: BLE001
        return ""
    else:
        return f"data:image/png;base64,{data}"


@dataclass
class DiagnosticInfo:
    """Container for diagnostic provenance data."""

    png_path: Path
    caption: str
    authors: list[str] = field(default_factory=list)
    plot_types: list[str] = field(default_factory=list)
    long_names: list[str] = field(default_factory=list)
    ancestors: list[str] = field(default_factory=list)
    recipe_name: str = ""
    realm: str = ""
    recipe_date: datetime = field(default_factory=datetime.now)
    relative_png_path: Path | None = None
    recipe_url: str = ""


@dataclass
class FilterOptions:
    """Container for filter options."""

    realms: set[str] = field(default_factory=set)
    plot_types: set[str] = field(default_factory=set)
    variables: set[str] = field(default_factory=set)
    authors: set[str] = field(default_factory=set)


def get_html_description(session: Session, date: datetime) -> str:
    """Create description of simulation(s) for HTML."""
    # Simulation-specific information
    simulations_info = session.simulations_info
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
    *,
    embed_images: bool = False,
) -> None:
    """Create summary HTML.

    Args:
        esmvaltool_output_dir: Path to the ESMValTool output directory
        description: Optional description to include in the HTML
        embed_images: If True, embed images as base64 for standalone HTML
    """
    # Extract all diagnostics with provenance
    diagnostics = _extract_all_diagnostics(esmvaltool_output_dir)
    filter_options = _get_filter_options(diagnostics)

    # Write the new dashboard HTML
    _write_dashboard_html(
        esmvaltool_output_dir,
        diagnostics,
        filter_options,
        description=description,
        embed_images=embed_images,
    )

    # Keep debug.html for backward compatibility
    _write_debug_html(esmvaltool_output_dir)

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


def _write_dashboard_html(
    output_dir: Path,
    diagnostics: list[DiagnosticInfo],
    filter_options: FilterOptions,
    description: str | None = None,
    *,
    embed_images: bool = False,
) -> None:
    """Write the new dashboard-style index.html.

    Args:
        output_dir: The ESMValTool output directory
        diagnostics: List of DiagnosticInfo objects
        filter_options: Filter options extracted from diagnostics
        description: Optional description to include in the HTML
        embed_images: If True, embed images as base64
    """
    if description is None:
        description = ""

    # Build filter options as JSON for JavaScript
    realms_json = sorted([r for r in filter_options.realms if r != "other"])
    plot_types_json = sorted(filter_options.plot_types)
    variables_json = sorted(filter_options.variables)
    authors_json = sorted(filter_options.authors)

    # Build card HTML for each diagnostic
    cards_html = []
    for diag in diagnostics:
        # Get image source (base64 or relative path)
        if embed_images and diag.png_path.exists():
            img_src = _embed_image_as_base64(diag.png_path)
        else:
            img_src = str(diag.relative_png_path) if diag.relative_png_path else ""

        # Build data attributes for filtering
        realm = diag.realm or "other"
        plot_type = ",".join(diag.plot_types) if diag.plot_types else "unknown"
        variables = ",".join(diag.long_names) if diag.long_names else "unknown"
        authors = ",".join(diag.authors) if diag.authors else "unknown"

        # Build provenance data for modal
        max_ancestors_shown = 5
        ancestors_html = "".join(
            f"<li>{Path(a).name}</li>" for a in diag.ancestors[:max_ancestors_shown]
        )
        if len(diag.ancestors) > max_ancestors_shown:
            ancestors_html += (
                f"<li>... and {len(diag.ancestors) - max_ancestors_shown} more</li>"
            )

        card = f"""\
        <div class="diagnostic-card col"
             data-realm="{realm}"
             data-plot-type="{plot_type}"
             data-variables="{variables}"
             data-authors="{authors}"
             data-caption="{_escape_html(diag.caption)}"
             data-recipe="{diag.recipe_name}">
            <div class="card h-100 shadow-sm">
                <div class="card-img-wrapper" style="cursor: pointer;"
                     onclick="openModal('{img_src}', '{_escape_html(diag.caption)}',
                         '{_escape_html(authors)}', '{_escape_html(plot_type)}',
                         '{_escape_html(variables)}', '{ancestors_html}',
                         '{diag.recipe_url}')">
                    <img src="{img_src}" class="card-img-top"
                         alt="{_escape_html(diag.caption)}">
                    <div class="card-img-overlay">
                        <i class="bi bi-arrows-fullscreen text-white fs-4"></i>
                    </div>
                </div>
                <div class="card-body">
                    <h6 class="card-title">
                        {_escape_html(diag.caption[:CAPTION_MAX_LENGTH])}
                        {"..." if len(diag.caption) > CAPTION_MAX_LENGTH else ""}
                    </h6>
                    <p class="card-text small text-muted">
                        <span class="badge bg-secondary">{realm}</span>
                        <span class="badge bg-info text-dark">{plot_type}</span>
                    </p>
                    <p class="card-text small">
                        <i class="bi bi-person"></i> {authors}
                    </p>
                </div>
            </div>
        </div>"""
        cards_html.append(card)

    cards_html_str = "\n".join(cards_html)

    # Build filter sidebar HTML
    def make_filter_checkboxes(items: list[str], name: str) -> str:
        if not items:
            return (
                f'<div class="mb-3">'
                f'<h6>{name}</h6>'
                f'<p class="text-muted small">None</p></div>'
            )
        items_html = []
        for item in items:
            checked = (
                "checked" if name == "Realm" and item in ("atmosphere", "all") else ""
            )
            items_html.append(
                f'<div class="form-check">'
                f'<input class="form-check-input filter-checkbox" type="checkbox" '
                f'value="{item}" id="filter-{name.lower()}-{item}" {checked}>'
                f'<label class="form-check-label" for="filter-{name.lower()}-{item}">'
                f"{item}</label></div>",
            )
        return f'<div class="mb-3"><h6>{name}</h6>{"".join(items_html)}</div>'

    sidebar_filters = f"""\
        {make_filter_checkboxes(realms_json, "Realm")}
        {make_filter_checkboxes(plot_types_json, "Plot Type")}
        {make_filter_checkboxes(variables_json, "Variables")}
        {make_filter_checkboxes(authors_json, "Authors")}
    """

    # Calculate stats
    total_diagnostics = len(diagnostics)
    total_recipes = len({d.recipe_name for d in diagnostics})

    # Render using Jinja2 template
    html = render_template(
        "dashboard.html",
        total_diagnostics=total_diagnostics,
        total_recipes=total_recipes,
        sidebar_filters=sidebar_filters,
        description=description,
        cards_html=cards_html_str,
    )

    index_file = output_dir / "index.html"
    index_file.write_text(html)
    logger.debug(f"Wrote dashboard to file://{index_file.resolve()}")


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


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
        index_name = _get_index_html_name(realm_of_button)
        button_style = (
            f"margin: 10px; padding: 20px; background-color: {background_color}; "
            f"width: 210px; border: none; box-shadow: none"
        )
        return textwrap.dedent(
            f"""\
            <div class="col-auto" style="width: 210px; margin: 10px;">
                <button
                    class="btn btn-primary btn-lg"
                    onclick="window.open('{index_name}', '_self')"
                    style="{button_style}"
                    id="{realm_of_button}"
                >
                    {_get_nice_realm_name(realm_of_button)}
                </button>
            </div>
            """,
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
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
                  rel="stylesheet"
                  integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"
                  crossorigin="anonymous">
            <link rel="stylesheet"
                  href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <title>ESMValTool results</title>
        </head>
        <body>
            <div class="container-fluid">
            <h1>
            <img src="https://github.com/ESMValGroup/ESMValTool/raw/main/doc/sphinx/source/figures/ESMValTool-logo-2.png"
                 class="img-fluid">
            </h1>
            <p>
            {description}
            Missing something? Have a look at the <a href=debug.html>debug page</a>.
            <p>
            <input class="form-control searchbox-input"
                   type="text"
                   placeholder="Type something here to search...">
            <div class="row">
                {realm_button("all")}
                {realm_button("atmosphere")}
                {realm_button("land")}
                {realm_button("ocean")}
                {realm_button("sanity-consistency-checks")}
            </div>
            <br>
            <div class="row row-cols-1 row-cols-md-3 g-4">
        """,
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
