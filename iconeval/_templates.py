"""Module that manages file templates."""

from __future__ import annotations

import os
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import yaml

from iconeval._config import ESMValToolConfig
from iconeval._recipe import Recipe

if TYPE_CHECKING:
    from collections.abc import Iterable

    from iconeval._simulation_info import SimulationInfo
    from iconeval._typing import FacetType, OptionValueType


# Note: Templates need to be hashable; thus, we use a frozen dataclass here
@dataclass(frozen=True, order=True)
class Template:
    """Base class for templates."""

    path: Path
    check_placeholders: bool = field(default=True, kw_only=True)
    content: str = field(init=False, repr=False, compare=False)
    name: str = field(init=False, repr=False, compare=False)

    REQUIRED_PLACEHOLDERS: ClassVar[tuple[str, ...]] = ()
    TEMPLATE_TYPE: ClassVar[str] = "template"

    def __post_init__(self) -> None:
        """Initialize class."""
        # See https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(
            self,
            "content",
            self._get_content(check_placeholders=self.check_placeholders),
        )
        object.__setattr__(self, "name", self.path.stem)

    def _check_placeholders(self, content: str) -> None:
        """Check that required placeholders are present."""
        for placeholder in self.REQUIRED_PLACEHOLDERS:
            if placeholder not in content:
                msg = (
                    f"{self.path} is not a valid {self.TEMPLATE_TYPE}, it "
                    f"needs to include '{placeholder}'"
                )
                raise ValueError(msg)

    def _deep_replace(
        self,
        obj: Any,
        old_value: str,
        new_value: FacetType,
    ) -> Any:
        """Replace value with other value in nested object (in-place)."""
        new_obj: Any

        # For dicts and lists, call _deep_replace recursively
        if isinstance(obj, dict):
            new_obj = {}
            for key, val in obj.items():
                key = self._deep_replace(key, old_value, new_value)
                new_obj[key] = self._deep_replace(val, old_value, new_value)
        elif isinstance(obj, list):
            new_obj = []
            for elem in obj:
                new_obj.append(self._deep_replace(elem, old_value, new_value))

        # For strings, actually replace values
        elif isinstance(obj, str):
            if obj == old_value:
                new_obj = new_value
            else:
                new_obj = obj.replace(old_value, str(new_value))

        # Otherwise, just return original object
        else:
            new_obj = obj

        return new_obj

    def _fill_placeholders(
        self,
        yaml_obj: Any,
        placeholders: dict[str, FacetType],
    ) -> Any:
        """Fill placeholders in a YAML object."""
        yaml_obj = deepcopy(yaml_obj)
        for placeholder, value in placeholders.items():
            new_value: Any

            # Replace Paths with str since yaml.safe_dump() cannot handle them
            if isinstance(value, dict):
                new_value = {}
                for key, val in value.items():
                    if isinstance(key, Path):
                        key = str(key)
                    if isinstance(val, Path):
                        val = str(val)
                    new_value[key] = val
                value = new_value
            elif isinstance(value, list):
                new_value = []
                for elem in value:
                    if isinstance(elem, Path):
                        elem = str(elem)
                    new_value.append(elem)
                value = new_value
            elif isinstance(value, Path):
                value = str(value)

            yaml_obj = self._deep_replace(yaml_obj, placeholder, value)
        return yaml_obj

    def _get_content(self, *, check_placeholders: bool) -> str:
        """Read content of file and check validity."""
        content = self.path.read_text()
        if check_placeholders:
            self._check_placeholders(content)
        return content


@dataclass(frozen=True, order=True)
class RecipeTemplate(Template):
    """Represents a recipe template."""

    dask_options: dict[str, OptionValueType] = field(
        init=False,
        repr=False,
        compare=False,
    )
    esmvaltool_options: dict[str, OptionValueType] = field(
        init=False,
        repr=False,
        compare=False,
    )
    srun_options: dict[str, OptionValueType] = field(
        init=False,
        repr=False,
        compare=False,
    )
    tags: list[str] = field(init=False, repr=False, compare=False)

    REQUIRED_PLACEHOLDERS = ("{{dataset_list}}",)
    TEMPLATE_TYPE = "recipe template"

    DASK_OPTIONS_MARKER: ClassVar[str] = "#DASK"
    ESMVALTOOL_OPTIONS_MARKER: ClassVar[str] = "#ESMVALTOOL"
    SRUN_OPTIONS_MARKER: ClassVar[str] = "#SRUN"
    TAGS_MARKER: ClassVar[str] = "#TAGS"

    def __post_init__(self) -> None:
        """Initialize class."""
        super().__post_init__()
        object.__setattr__(
            self,
            "dask_options",
            self._parse_additional_options(
                self.DASK_OPTIONS_MARKER,
                lstrip=True,
            ),
        )
        object.__setattr__(
            self,
            "esmvaltool_options",
            self._parse_additional_options(
                self.ESMVALTOOL_OPTIONS_MARKER,
            ),
        )
        object.__setattr__(
            self,
            "srun_options",
            self._parse_additional_options(
                self.SRUN_OPTIONS_MARKER,
            ),
        )
        object.__setattr__(self, "tags", self._parse_tags())

    def get_recipe(
        self,
        path: Path,
        simulations_info: list[SimulationInfo],
        **extra_facets: FacetType,
    ) -> Recipe:
        """Get recipe from template."""
        default_facets: dict[str, FacetType] = {
            "supplementary_variables": [
                {"short_name": "areacella", "skip": True},
                {"short_name": "areacello", "skip": True},
                {"short_name": "sftlf", "skip": True},
                {"short_name": "sftof", "skip": True},
            ],
        }

        # Determine facets for all simulations
        dataset_list: list[dict[str, FacetType]] = [
            {**default_facets, **s.guessed_facets} for s in simulations_info
        ]

        # Facets given via command line always take priority
        for dataset in dataset_list:
            dataset.update(extra_facets)

        # Fill placeholders
        timerange = extra_facets.get("timerange", "*")
        placeholders: dict[str, FacetType] = {
            "{{dataset}}": extra_facets.get("dataset", "ICON"),
            "{{dataset_list}}": dataset_list,
            "{{project}}": extra_facets.get("project", "ICON"),
            "{{timerange}}": timerange,
        }
        recipe_yaml = yaml.safe_load(self.content)
        recipe_yaml = self._fill_placeholders(recipe_yaml, placeholders)
        recipe_yaml = self._fill_alias_plot_kwargs(
            recipe_yaml,
            simulations_info,
            extra_facets,
        )

        # Write recipe (incl. magic comments like #ESMVALTOOL)
        recipe_content: str = "# ESMValTool\n"
        for dask_key, dask_value in self.dask_options.items():
            recipe_content += f"{self.DASK_OPTIONS_MARKER} --{dask_key}={dask_value}\n"
        for (
            esmvaltool_key,
            esmvaltool_value,
        ) in self.esmvaltool_options.items():
            recipe_content += (
                f"{self.ESMVALTOOL_OPTIONS_MARKER} "
                f"{esmvaltool_key}={esmvaltool_value}\n"
            )
        for srun_key, srun_value in self.srun_options.items():
            recipe_content += f"{self.SRUN_OPTIONS_MARKER} {srun_key}={srun_value}\n"
        for tag in self.tags:
            recipe_content += f"{self.TAGS_MARKER} {tag}\n"
        recipe_content += "---\n"
        recipe_content += yaml.safe_dump(recipe_yaml, sort_keys=False)
        path.write_text(recipe_content, encoding="utf-8")

        return Recipe(
            path=path,
            template=self,
            simulations_info=simulations_info,
            timerange=timerange,
        )

    def _fill_alias_plot_kwargs(
        self,
        obj: Any,
        simulations_info: list[SimulationInfo],
        extra_facets: dict[str, FacetType],
    ) -> Any:
        """Fill `{{alias_plot_kwargs}}` appropriately in recipe (in-place)."""
        # Possible aliases are:
        # -> {project}
        # -> {project}_{exp}
        # -> {project}_{dataset}
        # -> {project}_{dataset}_{exp}
        # These are determined by ESMValTool. For simplicity, we consider all
        # cases here (including dataset-specific facets and common facets).
        aliases: dict[FacetType, str] = {}  # map alias to color
        for idx, simulation_info in enumerate(simulations_info):
            exp = simulation_info.guessed_facets["exp"]
            if "project" in extra_facets:
                project = extra_facets["project"]
            else:
                project = simulation_info.guessed_facets["project"]
            if "dataset" in extra_facets:
                dataset = extra_facets["dataset"]
            else:
                dataset = simulation_info.guessed_facets["dataset"]
            color = f"C{idx}"

            # Avoid duplicates (always use first appearance)
            aliases.setdefault(project, color)
            aliases.setdefault(f"{project}_{exp}", color)
            aliases.setdefault(f"{project}_{dataset}", color)
            aliases.setdefault(f"{project}_{dataset}_{exp}", color)

        # Only replace {{alias_plot_kwargs}} if used as dictionary key
        new_obj: Any
        if isinstance(obj, dict):
            new_obj = {}
            for key, val in obj.items():
                val = self._fill_alias_plot_kwargs(
                    val,
                    simulations_info,
                    extra_facets,
                )
                if key == "{{alias_plot_kwargs}}":
                    for alias, color in aliases.items():
                        if isinstance(val, dict) and "color" not in val:
                            new_val = {**val, "color": color}
                        else:
                            new_val = val
                        new_obj[alias] = new_val
                else:
                    new_obj[key] = val

        elif isinstance(obj, list):
            new_obj = []
            for elem in obj:
                new_obj.append(
                    self._fill_alias_plot_kwargs(
                        elem,
                        simulations_info,
                        extra_facets,
                    ),
                )

        else:
            new_obj = obj

        return new_obj

    def _parse_additional_options(
        self,
        keyword: str,
        *,
        lstrip: bool = False,
    ) -> dict[str, OptionValueType]:
        """Parse additional options."""
        option_name = keyword.replace("#", "").lower()

        # Iterate over all recipe lines and find options
        options: dict[str, OptionValueType] = {}
        for line in self.content.split("\n"):
            original_line = line
            line = line.replace(" ", "")  # remove whitespace
            if not line.startswith(keyword):
                continue

            # Read option and check for errors
            line = line.replace(keyword, "")
            option = line.split("=")
            error_msg = (
                f"Invalid {option_name} option given in recipe template {self.path}: "
                f"'{original_line}', expected form '{keyword} --key=value' "
                f"(additional whitespace is fine)"
            )
            desired_option_length = 2
            if len(option) != desired_option_length:
                raise ValueError(error_msg)
            if not option[0].startswith("--"):
                raise ValueError(error_msg)

            # Try to cast option value to int/float and fill paths
            val: OptionValueType
            try:
                val = int(option[1])
            except ValueError:
                try:
                    val = float(option[1])
                except ValueError:
                    val = str(Path(os.path.expandvars(option[1])).expanduser())

            # Remove leading '--' if desired
            key = option[0].removeprefix("--") if lstrip else option[0]

            options[key] = val

        return options

    def _parse_tags(self) -> list[str]:
        """Parse tags."""
        tags: list[str] = []
        for line in self.content.split("\n"):
            if not line.startswith(self.TAGS_MARKER):
                continue
            tags.extend(line.replace(self.TAGS_MARKER, "").strip().split())
        for tag in tags:
            if tag.startswith("!"):
                msg = (
                    f"Found tag '{tag}' in recipe template {self.path}; tags "
                    f"must not start with '!'"
                )
                raise ValueError(msg)
        return tags


@dataclass(frozen=True, order=True)
class ESMValToolConfigTemplate(Template):
    """Represents an ESMValTool configuration template."""

    REQUIRED_PLACEHOLDERS = ()
    TEMPLATE_TYPE = "ESMValTool configuration template"

    def write_config(
        self,
        path: Path,
        simulations_info: list[SimulationInfo],
        output_dir: Path,
        dask_config: dict[str, Any],
    ) -> ESMValToolConfig:
        """Write ESMValTool configuration from template."""
        config_yaml = yaml.safe_load(self.content)

        # Add information from current ICONEval run
        config_yaml["dask"] = dask_config
        config_yaml["output_dir"] = str(output_dir)
        config_yaml = self._fill_projects(config_yaml, simulations_info)

        path.write_text(
            yaml.safe_dump(config_yaml, sort_keys=False),
            encoding="utf-8",
        )
        return ESMValToolConfig(
            path=path,
            template=self,
            simulations_info=simulations_info,
            output_dir=output_dir,
            dask_config=dask_config,
        )

    def _fill_projects(
        self,
        config_yaml: Any,
        simulations_info: list[SimulationInfo],
    ) -> Any:
        """Fill `projects` in ESMValTool configuration."""
        config_yaml = deepcopy(config_yaml)
        projects: dict[str, dict[str, Any]] = config_yaml.get("projects", {})

        # ICON
        icon_config: dict[str, Any] = {}
        for simulation_info in simulations_info:
            dirname_templates: dict[str, str] = {
                f"{simulation_info.exp}": "",
                f"{simulation_info.exp}-outdata": "outdata",
                f"{simulation_info.exp}-output": "output",
            }
            for data_name, dirname_template in dirname_templates.items():
                icon_config[data_name] = {
                    "dirname_template": dirname_template,
                    "filename_template": "{exp}_{var_type}*.nc",
                    "rootpath": str(simulation_info.path),
                    "type": "esmvalcore.io.local.LocalDataSource",
                }
        projects["ICON"] = {"data": icon_config}

        # EMAC
        emac_config: dict[str, Any] = {}
        for simulation_info in simulations_info:
            emac_config[simulation_info.exp] = {
                "dirname_template": "{channel}",
                "filename_template": "{exp}*{channel}{postproc_flag}.nc",
                "ignore_warnings": [
                    {
                        "message": r"Ignored formula of unrecognised type: .*",
                        "module": "iris",
                    },
                    {
                        "message": r"Ignoring formula terms variable .* referenced by "
                        "data variable .* via variable .*",
                        "module": "iris",
                    },
                    {
                        "message": r"Missing CF-netCDF formula term variable .*, "
                        "referenced by netCDF variable .*",
                        "module": "iris",
                    },
                    {
                        "message": r"NetCDF variable .* contains unknown cell method "
                        r".*",
                        "module": "iris",
                    },
                ],
                "rootpath": str(simulation_info.path),
                "type": "esmvalcore.io.local.LocalDataSource",
            }
        projects["EMAC"] = {"data": emac_config}

        config_yaml["projects"] = projects
        return config_yaml


def map_tags_to_recipes(
    recipe_template_paths: Iterable[Path],
) -> dict[str, list[RecipeTemplate]]:
    """Extract tags from recipe templates and map tags to recipe templates."""
    tag_map: dict[str, list[RecipeTemplate]] = defaultdict(list)
    for recipe_template_path in recipe_template_paths:
        recipe_template = RecipeTemplate(recipe_template_path)
        for tag in recipe_template.tags:
            tag_map[tag].append(recipe_template)
    return tag_map
