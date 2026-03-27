"""Module that manages IO directories and files for ICON output evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from loguru import logger

from iconeval._job import Job
from iconeval._simulation_info import SimulationInfo
from iconeval._templates import (
    ESMValToolConfigTemplate,
    RecipeTemplate,
    map_tags_to_recipes,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from iconeval._typing import FacetType, OptionValueType


logger = logger.opt(colors=True)


class Session:
    """Manage ICONEval session."""

    PROJECT_ROOT_DIR: ClassVar[Path] = Path(str(files("iconeval"))).resolve()

    CFG_TEMPLATE: ClassVar[Path] = PROJECT_ROOT_DIR / "esmvaltool_config_template.yml"
    DEFAULT_RECIPE_TEMPLATE_DIR: ClassVar[Path] = PROJECT_ROOT_DIR / "recipe_templates"

    DEFAULT_OUTPUT_DIR_NAME: ClassVar[str] = "output_iconeval"
    OUTPUT_DIR_CONFIG: ClassVar[str] = "config"
    OUTPUT_DIR_ESMVALTOOL: ClassVar[str] = "esmvaltool_output"
    OUTPUT_DIR_RECIPES: ClassVar[str] = "recipes"
    OUTPUT_DIR_SLURM: ClassVar[str] = "slurm"

    def __init__(
        self,
        input_dirs: Iterable[str | Path],
        parent_output_dir: str | Path | None,
        name: str | None,
    ) -> None:
        """Initialize class."""
        self._simulations_info = [
            SimulationInfo.from_path(p) for p in self._get_input_dirs(input_dirs)
        ]
        if name is None:
            name = "_".join([s.exp for s in self.simulations_info])
        self._name = name

        logger.info(f"Evaluation name: <magenta>{self.name}</magenta>")
        logger.info("")
        logger.info("Input directories:")
        logger.info("------------------")
        for sim_info in self.simulations_info:
            logger.info(f"- <magenta>{sim_info.exp}</magenta>")
            logger.info(f"  (Path: <cyan>{sim_info.path}</cyan>)")
        logger.info("")

        # Set up output directories
        self._output_dir = self._get_output_dir(parent_output_dir)
        logger.info(f"Output directory: <cyan>{self.output_dir}</cyan>")
        logger.debug(f"Configuration: {self.output_dir_config}")
        logger.debug(f"ESMValTool: {self.output_dir_esmvaltool}")
        logger.debug(f"Recipes: {self.output_dir_recipes}")
        logger.debug(f"Slurm: {self.output_dir_slurm}")
        logger.info("")

    def __repr__(self) -> str:
        """Return string representation of class instance."""
        return (
            f"Session(input_dirs={self.input_dirs!r}, "
            f"output_dir={self.output_dir!r}, name={self.name!r})"
        )

    @property
    def input_dirs(self) -> list[Path]:
        """Input directory."""
        return [s.path for s in self.simulations_info]

    @property
    def output_dir(self) -> Path:
        """Output directory."""
        return self._output_dir

    @property
    def output_dir_config(self) -> Path:
        """Configuration output directory."""
        output_dir = self.output_dir / self.OUTPUT_DIR_CONFIG
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @property
    def output_dir_esmvaltool(self) -> Path:
        """Output directory."""
        output_dir = self.output_dir / self.OUTPUT_DIR_ESMVALTOOL
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @property
    def output_dir_recipes(self) -> Path:
        """Recipes output directory."""
        output_dir = self.output_dir / self.OUTPUT_DIR_RECIPES
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @property
    def output_dir_slurm(self) -> Path:
        """Slurm output directory."""
        output_dir = self.output_dir / self.OUTPUT_DIR_SLURM
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @property
    def name(self) -> str:
        """Session name."""
        return self._name

    @property
    def simulations_info(self) -> list[SimulationInfo]:
        """Information about simulations."""
        return self._simulations_info

    def get_jobs(
        self,
        *,
        recipe_template_paths: str | Path | Iterable[str | Path] | None,
        always_use_default_recipe_templates: bool,
        account: str,
        dask: bool,
        esmvaltool_executable: str,
        srun_executable: str,
        ignore_recipe_esmvaltool_options: bool,
        ignore_recipe_srun_options: bool,
        ignore_recipe_dask_options: bool,
        additional_esmvaltool_options: dict | None,
        additional_srun_options: dict | None,
        additional_dask_options: dict | None,
        tags: str | list[str] | None,
        **extra_facets: FacetType,
    ) -> list[Job]:
        """Get jobs."""
        # Get templates
        esmvaltool_config_template = ESMValToolConfigTemplate(
            self.CFG_TEMPLATE,
        )
        recipe_templates = self._get_recipe_templates(
            recipe_template_paths,
            tags,
            always_use_default_recipe_templates=always_use_default_recipe_templates,
        )

        logger.debug(
            f"ESMValTool configuration template: {esmvaltool_config_template.path}",
        )
        logger.debug("")

        # Setup jobs
        jobs: list[Job] = []
        for recipe_template in recipe_templates:
            recipe = recipe_template.get_recipe(
                self.output_dir_recipes / recipe_template.path.name,
                self.simulations_info,
                **extra_facets,
            )
            dask_config = self._get_dask_config(
                recipe_template,
                account,
                additional_dask_options,
                dask=dask,
                ignore_recipe_dask_options=ignore_recipe_dask_options,
            )
            esmvaltool_config_dir = self.output_dir_config / recipe_template.name
            esmvaltool_config_dir.mkdir(parents=True, exist_ok=True)
            esmvaltool_config_path = esmvaltool_config_dir / "config-user.yml"
            esmvaltool_config = esmvaltool_config_template.write_config(
                esmvaltool_config_path,
                recipe.simulations_info,
                self.output_dir_esmvaltool,
                dask_config,
            )
            job = Job(
                recipe=recipe,
                esmvaltool_config=esmvaltool_config,
                account=account,
                esmvaltool_executable=esmvaltool_executable,
                srun_executable=srun_executable,
                ignore_recipe_esmvaltool_options=ignore_recipe_esmvaltool_options,
                ignore_recipe_srun_options=ignore_recipe_srun_options,
                additional_esmvaltool_options=additional_esmvaltool_options,
                additional_srun_options=additional_srun_options,
                output_dir_slurm=self.output_dir_slurm,
            )
            jobs.append(job)

        return jobs

    def _get_dask_config(
        self,
        recipe_template: RecipeTemplate,
        account: str,
        additional_dask_options: dict | None,
        *,
        dask: bool,
        ignore_recipe_dask_options: bool,
    ) -> dict[str, Any]:
        """Get ESMValTool dask configuration."""
        dask_config: dict[str, Any] = {}

        # If default dask scheduler is desired, use empty dask configuration
        if not dask:
            return dask_config

        # Remove leading '--' from keys of additional dask options
        if additional_dask_options is None:
            additional_dask_options = {}
        additional_dask_options = {
            k.removeprefix("--"): v for (k, v) in additional_dask_options.items()
        }

        # Get user-specific options
        user_options: dict[str, OptionValueType] = {}
        user_options.update(additional_dask_options)
        if not ignore_recipe_dask_options:
            user_options.update(recipe_template.dask_options)

        # Only use default options when type is distributed.LocalCluster
        scheduler_type = user_options.get("type", "distributed.LocalCluster")
        cluster_options: dict[str, OptionValueType] = {}
        if scheduler_type == "distributed.LocalCluster":
            cluster_options.update(
                {
                    "memory_limit": "3880MB",  # 2x memory per CPU from srun
                    "n_workers": 8,
                    "threads_per_worker": 2,
                    "type": "distributed.LocalCluster",
                },
            )

        cluster_options.update(user_options)

        # Update account for SLURMCluster
        if cluster_options.get("type") == "dask_jobqueue.SLURMCluster":
            cluster_options["account"] = account

        dask_config.update(
            {
                "use": "iconeval",
                "profiles": {
                    "iconeval": {
                        "cluster": cluster_options,
                    },
                },
            },
        )

        return dask_config

    def _get_input_dirs(self, input_dirs: Iterable[str | Path]) -> list[Path]:
        """Get input directories."""
        if not input_dirs:
            msg = "No input directory given"
            raise ValueError(msg)

        # Check input directories
        input_dir_paths: list[Path] = []
        for input_dir in input_dirs:
            input_dir = Path(input_dir).expanduser().resolve()
            if not input_dir.is_dir():
                msg = f"Input directory '{input_dir}' does not exist"
                raise NotADirectoryError(msg)
            input_dir_paths.append(input_dir)

        # Make sure that no duplicate experiments exists
        exps = [d.name for d in input_dir_paths]
        if len(exps) != len(set(exps)):
            msg = (
                f"Multiple experiments with the same name are not supported, got {exps}"
            )
            raise ValueError(msg)

        return input_dir_paths

    def _get_output_dir(self, parent_output_dir: str | Path | None) -> Path:
        """Get output directory."""
        now = datetime.now(UTC).strftime("%Y%m%d_%H%M%SUTC")
        if parent_output_dir is None:
            parent_output_dir = Path.cwd() / self.DEFAULT_OUTPUT_DIR_NAME
        output_dir = Path(parent_output_dir) / f"{self.name}_{now}"
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _get_recipe_templates(
        self,
        recipe_template_paths: str | Path | Iterable[str | Path] | None,
        tags: str | list[str] | None,
        *,
        always_use_default_recipe_templates: bool,
    ) -> list[RecipeTemplate]:
        """Get recipe templates."""
        logger.debug("Recipe templates:")
        logger.debug("-----------------")
        recipe_template_list: list[Path] = []

        # Use default templates if none are specified or
        # always_use_default_recipe_templates is True
        if recipe_template_paths is None or always_use_default_recipe_templates:
            logger.debug(
                f"Using default recipe templates from directory "
                f"{self.DEFAULT_RECIPE_TEMPLATE_DIR}",
            )
            recipe_template_list.extend(
                self.DEFAULT_RECIPE_TEMPLATE_DIR.rglob("*.yml"),
            )

        # Add user-defined recipe templates
        if isinstance(recipe_template_paths, (str, Path)):
            recipe_template_paths = [recipe_template_paths]
        if recipe_template_paths is not None:
            recipe_template_list.extend(
                Path(p).expanduser().resolve() for p in recipe_template_paths
            )

        # Resolve globs and Remove duplicates
        recipe_template_list = self._resolve_globs(recipe_template_list)
        recipe_template_list = list(set(recipe_template_list))

        # Check if recipe templates exist
        for recipe_template_path in recipe_template_list:
            if not recipe_template_path.is_file():
                msg = f"No recipe template matching '{recipe_template_path}' found"
                raise FileNotFoundError(msg)

        # Filter recipe templates according to tags
        recipe_templates: list[RecipeTemplate]
        if isinstance(tags, str):
            tags = [tags]
        if tags is None:
            recipe_templates = [RecipeTemplate(r) for r in recipe_template_list]
        else:
            tag_map = map_tags_to_recipes(recipe_template_list)
            unique_recipe_templates: set[RecipeTemplate] = set()
            select_tags: list[str] = []
            deselect_tags: list[str] = []
            for tag in tags:
                if tag.startswith("!"):
                    deselect_tags.append(tag[1:])
                else:
                    select_tags.append(tag)

            # Select tags; if there are no tags to select recipes, use all
            if not select_tags:
                unique_recipe_templates = {
                    RecipeTemplate(r) for r in recipe_template_list
                }
            else:
                for tag in select_tags:
                    unique_recipe_templates |= set(tag_map.get(tag, []))

            # Deselect tags
            for tag in deselect_tags:
                for recipe_template in tag_map.get(tag, []):
                    unique_recipe_templates.discard(recipe_template)

            recipe_templates = list(unique_recipe_templates)

        # Check if recipes remained; if yes, sort and log them
        if not recipe_templates:
            if tags is not None:
                msg = f"No recipe templates for tags {tags} given"
            else:
                msg = "No recipe templates given"
            raise ValueError(msg)
        recipe_templates = sorted(recipe_templates)
        for recipe_template in recipe_templates:
            logger.debug(f"  - {recipe_template.path}")
        logger.debug("")

        return recipe_templates

    @staticmethod
    def _resolve_globs(paths: Iterable[Path]) -> list[Path]:
        """Resolve globs in paths."""
        resolved_paths: list[Path] = []

        for path in paths:
            glob = list(path.parent.glob(path.name))

            # If a path does not resolve into a valid path, ignore it here and
            # raise a proper error later
            if not glob:
                resolved_paths.append(path)
                continue

            resolved_paths.extend(glob)

        return resolved_paths
