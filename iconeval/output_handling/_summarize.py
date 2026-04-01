"""Create summary HTML for ESMValTool runs."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from loguru import logger

import iconeval
from iconeval import get_user_name
from iconeval._templates import RecipeTemplate
from iconeval.output_handling._html_templates import render_template

if TYPE_CHECKING:
    from collections.abc import Iterable

    from iconeval._simulation_info import SimulationInfo


logger = logger.opt(colors=True)


def get_simulations_info_html(simulations_info: Iterable[SimulationInfo]) -> str:
    """Create nice HTML output of simulation(s)."""
    sim_chips = []
    for sim_info in simulations_info:
        namelist_items = "".join(f"<li>{path}</li>" for path in sim_info.namelist_files)
        sim_chips.append(
            f"<span class='sim-chip' onclick=\"openSimModal("
            f"'{_escape_html(sim_info.exp)}', "
            f"'{_escape_html(str(sim_info.path))}', "
            f"'{_escape_html(sim_info.owner)}', "
            f"'{_escape_html(sim_info.date)}', "
            f"'{_escape_html(sim_info.grid_info)}', "
            f"'{namelist_items}')\">"
            f"{sim_info.exp}</span>",
        )

    simulations_html = "".join(sim_chips)

    return (
        f"<div class='sim-info-label'>Simulations:</div>\n"
        f"<div class='sim-chips'>{simulations_html}</div>\n"
    )


def summarize(
    esmvaltool_output_dir: Path,
    date: datetime | None = None,
    user: str | None = None,
    description: str | None = None,
    *,
    embed_images: bool = False,
) -> None:
    """Create summary HTML."""
    if date is None:
        date = datetime.now(UTC)
    if user is None:
        user = get_user_name()

    diagnostics = _extract_all_diagnostics(esmvaltool_output_dir)
    filter_options = _get_filter_options(diagnostics)
    recipes = _extract_all_recipes(esmvaltool_output_dir)

    _write_dashboard_html(
        output_dir=esmvaltool_output_dir,
        diagnostics=diagnostics,
        filter_options=filter_options,
        recipes=recipes,
        date=date,
        user=user,
        description=description,
        embed_images=embed_images,
    )

    logger.info(
        f"Successfully created summary HTML "
        f"<cyan>{esmvaltool_output_dir / 'index.html'}</cyan>",
    )


@dataclass(frozen=True, kw_only=True, order=True)
class _DiagnosticInfo:
    """Container for diagnostic provenance data."""

    img_path: Path
    relative_img_path: Path = field(repr=False, compare=False)
    caption: str = field(repr=False, compare=False)
    plot_types: tuple[str, ...] = field(repr=False, compare=False)
    long_names: tuple[str, ...] = field(repr=False, compare=False)
    input_datasets: tuple[str, ...] = field(repr=False, compare=False)
    recipe_name: str = field(repr=False, compare=False)
    realm: str = field(repr=False, compare=False)

    @classmethod
    def from_recipe_dir(
        cls,
        recipe_dir: Path,
        output_dir: Path,
    ) -> list[_DiagnosticInfo]:
        """Load all diagnostics from recipe directory."""
        recipe_name = _get_recipe_name(recipe_dir)

        # Determine realm from recipe tags
        realm = "other"
        recipe_file = recipe_dir / "run" / f"recipe_{recipe_name}.yml"
        if recipe_file.exists():
            try:
                template = RecipeTemplate(recipe_file, check_placeholders=False)
            except Exception:  # noqa: BLE001
                logger.debug(f"Could not load recipe template {recipe_file}")
            else:
                for tag in template.tags:
                    realm_tags = (
                        "atmosphere",
                        "ocean",
                        "land",
                        "sanity-consistency-checks",
                    )
                    if tag in realm_tags:
                        realm = tag
                        break

        # Get all diagnostics from provenance output
        diagnostics: list[_DiagnosticInfo] = []
        for prov_file in (recipe_dir / "run").rglob("diagnostic_provenance.yml"):
            provenance_record = _read_diagnostic_provenance(prov_file)
            for img_str, img_provenance in provenance_record.items():
                img_path = Path(img_str)
                if img_path.suffix != ".png":  # only PNGs are supported for now
                    continue
                if not img_path.exists():
                    logger.warning(
                        f"Figure included in provenance file {prov_file} does not "
                        f"exist",
                    )
                    continue
                try:
                    relative_img_path = img_path.relative_to(output_dir)
                except ValueError:
                    logger.warning(
                        f"Figure is outside of output directory {output_dir}",
                    )
                    continue

                diagnostics.append(
                    cls(
                        img_path=img_path,
                        relative_img_path=relative_img_path,
                        caption=img_provenance.get("caption", ""),
                        plot_types=tuple(img_provenance.get("plot_types", [])),
                        long_names=tuple(img_provenance.get("long_names", [])),
                        input_datasets=tuple(img_provenance.get("ancestors", [])),
                        recipe_name=recipe_name,
                        realm=realm,
                    ),
                )
        logger.debug(
            f"Found {len(diagnostics)} diagnostics included in provenance "
            f"files of recipe {recipe_name}",
        )

        return sorted(diagnostics)


@dataclass(frozen=True, kw_only=True, order=True)
class _RecipeInfo:
    """Container for recipe information including diagnostics."""

    name: str
    date: datetime = field(compare=False)
    success: bool = field(compare=False)
    diagnostics: tuple[_DiagnosticInfo, ...] = field(repr=False, compare=False)


@dataclass(frozen=True, kw_only=True)
class _FilterOptions:
    """Container for filter options."""

    realms: frozenset[str]
    plot_types: frozenset[str]
    variables: frozenset[str]
    recipe_names: frozenset[str]


def _crop_text(text: str, max_text_length: int = 100) -> str:
    """Crop text."""
    return text[:max_text_length] + "..." if len(text) > max_text_length else text


def _embed_image_as_base64(img_path: Path) -> str:
    """Embed PNG image as base64 data URL."""
    img_type = img_path.suffix[1:]
    try:
        with img_path.open("rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
    except Exception:  # noqa: BLE001
        return ""
    else:
        return f"data:image/{img_type};base64,{data}"


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _extract_all_diagnostics(output_dir: Path) -> list[_DiagnosticInfo]:
    """Extract all diagnostics with their provenance data."""
    diagnostics: list[_DiagnosticInfo] = []
    for recipe_dir in Path(output_dir).glob("recipe_*"):
        diagnostics.extend(_DiagnosticInfo.from_recipe_dir(recipe_dir, output_dir))
    return sorted(diagnostics)


def _extract_all_recipes(output_dir: Path) -> list[_RecipeInfo]:
    """Extract all recipes with their diagnostics."""
    recipes: list[_RecipeInfo] = []

    for recipe_dir in Path(output_dir).glob("recipe_*"):
        log = recipe_dir / "run" / "main_log.txt"
        if log.exists() and "Run was successful\n" in log.read_text():
            success = True
        else:
            success = False
        recipe_name = _get_recipe_name(recipe_dir)
        recipe_date = _get_recipe_date(recipe_dir)
        diagnostics = _DiagnosticInfo.from_recipe_dir(recipe_dir, output_dir)

        recipes.append(
            _RecipeInfo(
                name=recipe_name,
                date=recipe_date,
                success=success,
                diagnostics=tuple(diagnostics),
            ),
        )
    logger.debug(f"Found {len(recipes)} recipes")

    return sorted(recipes)


def _get_filter_options(diagnostics: list[_DiagnosticInfo]) -> _FilterOptions:
    """Extract unique filter values from diagnostics."""
    realms: set[str] = set()
    plot_types: set[str] = set()
    variables: set[str] = set()
    recipe_names: set[str] = set()

    for diag in diagnostics:
        realms.add(diag.realm)
        plot_types.update(diag.plot_types)
        variables.update(diag.long_names)
        recipe_names.add(diag.recipe_name)

    return _FilterOptions(
        realms=frozenset(realms),
        plot_types=frozenset(plot_types),
        variables=frozenset(variables),
        recipe_names=frozenset(recipe_names),
    )


def _get_open_modal_str(
    img_src: str,
    caption: str,
    plot_types: str,
    variables: str,
    input_datasets: str,
    recipe_name: str,
) -> str:
    """Return string used for opening modals."""
    return (
        f"openModal('{img_src}', '{_escape_html(caption)}', "
        f"'{_escape_html(plot_types)}', '{_escape_html(variables)}', "
        f"'{input_datasets}', '{recipe_name}')"
    )


def _get_recipe_date(recipe_dir: Path) -> datetime:
    """Extract recipe date from output dir."""
    date_pattern = r"(?P<datetime>[0-9]{8}_[0-9]{6})-?[0-9]*$"
    regex = re.search(date_pattern, recipe_dir.stem)
    if regex is not None:
        date_str = regex.group("datetime")
        return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
    return datetime.now(UTC)


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


def _read_diagnostic_provenance(provenance_file: Path) -> dict[str, Any]:
    """Read diagnostic_provenance.yml file."""
    try:
        with provenance_file.open() as f:
            provenance_record = yaml.safe_load(f)
    except yaml.YAMLError:
        logger.warning(f"Could not parse {provenance_file}")
        return {}
    else:
        return provenance_record or {}


def _write_dashboard_html(
    *,
    output_dir: Path,
    diagnostics: list[_DiagnosticInfo],
    filter_options: _FilterOptions,
    recipes: list[_RecipeInfo],
    date: datetime,
    user: str,
    description: str | None = None,
    embed_images: bool = False,
) -> None:
    """Write dashboard-style index.html."""
    if description is None:
        description = ""

    # Build filter options as JSON for JavaScript
    realms_json = sorted([r for r in filter_options.realms if r != "other"])
    plot_types_json = sorted(filter_options.plot_types)
    variables_json = sorted(filter_options.variables)
    recipe_names_json = sorted(filter_options.recipe_names)

    # Build card HTML for each diagnostic
    cards_html = []
    for diag in diagnostics:
        # Get image source (base64 or relative path)
        if embed_images and diag.img_path.exists():
            img_src = _embed_image_as_base64(diag.img_path)
        else:
            img_src = str(diag.relative_img_path) if diag.relative_img_path else ""

        # Build data attributes for filtering (comma-separated for filtering logic)
        realm = diag.realm or "other"
        plot_types = ",".join(diag.plot_types) if diag.plot_types else "unknown"
        variables = ",".join(diag.long_names) if diag.long_names else "unknown"

        # Build individual badges for plot types and variables
        plot_type_badges = (
            "".join(
                f'<span class="badge bg-success clickable"\n'
                f"      onclick=\"toggleFilterBadge('plot_types', '{pt}')\">{pt}\n"
                f"</span>"
                for pt in diag.plot_types
            )
            if diag.plot_types
            else '<span class="badge bg-success">unknown</span>'
        )

        variable_badges = (
            "".join(
                f'<span class="badge bg-info clickable"\n'
                f"      onclick=\"toggleFilterBadge('variables', '{v}')\">{v}\n"
                f"</span>"
                for v in diag.long_names
            )
            if diag.long_names
            else '<span class="badge bg-info">unknown</span>'
        )

        # Build provenance data for modal
        max_input_datasets_shown = 5
        input_datasets_html = "".join(
            f"<li>{Path(a).name}</li>"
            for a in diag.input_datasets[:max_input_datasets_shown]
        )
        if len(diag.input_datasets) > max_input_datasets_shown:
            input_datasets_html += (
                f"<li>... and {len(diag.input_datasets) - max_input_datasets_shown} "
                f"more</li>"
            )

        card = f"""\
        <div class="diagnostic-card col"
             data-realm="{realm}"
             data-plot-type="{plot_types}"
             data-variables="{variables}"
             data-caption="{_escape_html(diag.caption)}"
             data-recipe="{diag.recipe_name}">
            <div class="card h-100 shadow-sm">
                <div class="card-img-wrapper" style="cursor: pointer;"
                     onclick="{_get_open_modal_str(img_src, diag.caption, plot_types, variables, input_datasets_html, diag.recipe_name)}">
                    <img src="{img_src}" class="card-img-top"
                         alt="{_escape_html(diag.caption)}">
                    <div class="card-img-overlay">
                        <i class="bi bi-arrows-fullscreen text-white fs-4"></i>
                    </div>
                </div>
                <div class="card-body">
                    <h6 class="card-title">
                        {_escape_html(_crop_text(diag.caption))}
                    </h6>
                    <p class="card-text small text-muted">
                        <span class="badge bg-primary clickable"
                              onclick="toggleFilterBadge('realm', '{realm}')">{realm}
                        </span>
                        {plot_type_badges}
                        {variable_badges}
                        <span class="badge bg-warning text-dark clickable"
                              onclick="toggleFilterBadge('recipe', '{diag.recipe_name}')">{diag.recipe_name}
                        </span>
                    </p>
                </div>
            </div>
        </div>"""  # noqa: E501
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
            checked = ""
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
        {make_filter_checkboxes(plot_types_json, "Plot Types")}
        {make_filter_checkboxes(variables_json, "Variables")}
        {make_filter_checkboxes(recipe_names_json, "Recipe")}
    """

    # Build recipes HTML for the modal
    def make_recipe_item(recipe: _RecipeInfo) -> str:
        """Build HTML for a single recipe in the modal."""
        status_class = "bg-success" if recipe.success else "bg-danger"
        status_text = "Success" if recipe.success else "Failed"
        diag_count = len(recipe.diagnostics)

        # Build diagnostics list for this recipe (clickable to open modal)
        diag_items = ""
        for diag in recipe.diagnostics:
            img_src = str(diag.relative_img_path) if diag.relative_img_path else ""
            plot_types = ",".join(diag.plot_types) if diag.plot_types else ""
            variables = ",".join(diag.long_names) if diag.long_names else ""
            input_datasets = "".join(
                f"<li>{Path(a).name}</li>" for a in diag.input_datasets
            )
            diag_items += (
                f"<li class='clickable' "
                f'onclick="closeRecipesModal(); '
                f"{
                    _get_open_modal_str(
                        img_src,
                        diag.caption,
                        plot_types,
                        variables,
                        input_datasets,
                        diag.recipe_name,
                    )
                }"
                f'">{_escape_html(_crop_text(diag.caption, 60))}</li>'
            )
        if diag_items:
            diag_items = f'<ul class="detail-list-plain mt-2">{diag_items}</ul>'

        return f"""\
            <div class="recipe-item mb-3">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>{recipe.name}</strong>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
                <div class="small text-muted">{diag_count} diagnostic(s)</div>
                {diag_items}
            </div>"""

    recipes_html = "".join(make_recipe_item(r) for r in sorted(recipes))

    # Format date for display
    formatted_date = date.strftime("%Y-%m-%d %H:%M")

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
        recipes_html=recipes_html,
        version=iconeval.__version__,
        evaluation_date=formatted_date,
        evaluation_user=user,
    )

    # Strip trailing whitespace from each line and ensure single newline at end
    lines = html.splitlines()
    html = "\n".join(line.rstrip() for line in lines) + "\n"

    index_file = output_dir / "index.html"
    index_file.write_text(html, newline="\n")
    logger.debug(f"Wrote dashboard to file://{index_file.resolve()}")
