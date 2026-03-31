"""Create summary HTML for ESMValTool runs."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from loguru import logger

import iconeval
from iconeval import get_user_name
from iconeval._templates import RecipeTemplate
from iconeval.output_handling._templates_html import render_template

if TYPE_CHECKING:
    from iconeval._session import Session

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
            data = yaml.safe_load(f)
    except yaml.YAMLError:
        logger.warning(f"Could not parse {provenance_file}")
        return {}
    else:
        return data or {}


def _extract_all_diagnostics(output_dir: Path) -> list[DiagnosticInfo]:
    """Extract all diagnostics with their provenance data.

    PNGs are in plots/<diagnostic>/plot/*.png
    Provenance is in run/<diagnostic>/plot/diagnostic_provenance.yml

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


def get_html_description(session: Session, date: datetime) -> str:
    """Create description of simulation(s) for HTML."""
    simulations_info = session.simulations_info
    current_user = get_user_name()

    # Build simulation chips (clickable cards for each simulation)
    sim_chips = []
    for i, sim_info in enumerate(simulations_info):
        namelist_items = "".join(
            f"<li>{path}</li>" for path in sim_info.namelist_files
        )
        sim_chips.append(
            f"<span class='sim-chip' onclick=\"openSimModal("
            f"'{_escape_html(sim_info.exp)}', "
            f"'{_escape_html(str(sim_info.path))}', "
            f"'{_escape_html(sim_info.owner)}', "
            f"'{_escape_html(sim_info.date)}', "
            f"'{_escape_html(sim_info.grid_info)}', "
            f"'{namelist_items}')\">"
            f"{sim_info.exp}</span>"
        )

    simulations_html = "".join(sim_chips)

    return (
        f"<div class='description-section'>\n"
        f"  <div class='sim-info-header'>\n"
        f"    <div>\n"
        f"      <span class='sim-info-label'>Evaluated by</span>\n"
        f"      <span class='sim-info-value'>{current_user}</span>\n"
        f"    </div>\n"
        f"    <div>\n"
        f"      <span class='sim-info-label'>Evaluation date</span>\n"
        f"      <span class='sim-info-value'>{date.strftime('%Y-%m-%d %H:%M')}</span>\n"
        f"    </div>\n"
        f"  </div>\n"
        f"  <div class='sim-info-label'>Simulations</div>\n"
        f"  <div class='sim-chips'>{simulations_html}</div>\n"
        f"</div>"
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

    logger.info(
        f"Successfully created summary HTML "
        f"<cyan>{esmvaltool_output_dir / 'index.html'}</cyan>",
    )


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


def _write_dashboard_html(
    output_dir: Path,
    diagnostics: list[DiagnosticInfo],
    filter_options: FilterOptions,
    description: str | None = None,
    *,
    embed_images: bool = False,
) -> None:
    """Write dashboard-style index.html."""
    if description is None:
        description = ""

    # Build filter options as JSON for JavaScript
    realms_json = sorted([r for r in filter_options.realms if r != "other"])
    plot_types_json = sorted(filter_options.plot_types)
    variables_json = sorted(filter_options.variables)

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
             data-caption="{_escape_html(diag.caption)}"
             data-recipe="{diag.recipe_name}">
            <div class="card h-100 shadow-sm">
                <div class="card-img-wrapper" style="cursor: pointer;"
                     onclick="openModal('{img_src}', '{_escape_html(diag.caption)}',
                         '{_escape_html(plot_type)}',
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
                f"<h6>{name}</h6>"
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
        has_description=bool(description),
        cards_html=cards_html_str,
        version=iconeval.__version__,
    )

    # Strip trailing whitespace from each line and ensure single newline at end
    lines = html.splitlines()
    html = "\n".join(line.rstrip() for line in lines) + "\n"

    index_file = output_dir / "index.html"
    index_file.write_text(html, newline="\n")
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
