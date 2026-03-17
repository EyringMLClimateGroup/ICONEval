"""Module that manages jobs."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from pathlib import Path

    from iconeval._config import ESMValToolConfig
    from iconeval._recipe import Recipe
    from iconeval._typing import OptionValueType


logger = logger.opt(colors=True)


class Job:
    """Class representing ESMValTool job (i.e., one single recipe run)."""

    def __init__(
        self,
        *,
        recipe: Recipe,
        esmvaltool_config: ESMValToolConfig,
        account: str,
        esmvaltool_executable: str,
        srun_executable: str,
        ignore_recipe_esmvaltool_options: bool,
        ignore_recipe_srun_options: bool,
        additional_esmvaltool_options: dict | None,
        additional_srun_options: dict | None,
        output_dir_slurm: Path,
    ) -> None:
        """Initialize class."""
        if additional_esmvaltool_options is None:
            additional_esmvaltool_options = {}
        if additional_srun_options is None:
            additional_srun_options = {}

        self._recipe = recipe
        self._esmvaltool_config = esmvaltool_config
        self._account = account
        self._esmvaltool_executable = esmvaltool_executable
        self._srun_executable = srun_executable
        self._ignore_recipe_esmvaltool_options = ignore_recipe_esmvaltool_options
        self._ignore_recipe_srun_options = ignore_recipe_srun_options
        self._additional_esmvaltool_options = additional_esmvaltool_options
        self._additional_srun_options = additional_srun_options
        self._output_dir_slurm = output_dir_slurm

    def __repr__(self) -> str:
        """Return string representation of class instance."""
        return (
            f"Job({self.recipe!r}, "
            f"esmvaltool_config={self.esmvaltool_config!r}, "
            f"account={self.account!r})"
        )

    def __str__(self) -> str:
        """Return nicely readable representation of class instance."""
        return f"Job {self.recipe.name}"

    @property
    def account(self) -> str:
        """Account which is used to charge for Slurm jobs."""
        return self._account

    @property
    def esmvaltool_config(self) -> ESMValToolConfig:
        """ESMValTool configuration."""
        return self._esmvaltool_config

    @property
    def esmvaltool_executable(self) -> str:
        """ESMValTool executable."""
        return self._esmvaltool_executable

    @property
    def esmvaltool_options(self) -> dict[str, OptionValueType]:
        """Command line arguments for ESMValTool."""
        options: dict[str, OptionValueType] = {}
        options.update(self._additional_esmvaltool_options)
        if not self._ignore_recipe_esmvaltool_options:
            options.update(self.recipe.template.esmvaltool_options)
        return options

    @property
    def output_dir(self) -> Path | None:
        """ESMValTool output directory."""
        pattern = f"{self.recipe.name}_*"
        dir_glob = list(self.esmvaltool_config.output_dir.glob(pattern))
        if not dir_glob:
            return None
        return dir_glob[0]

    @property
    def recipe(self) -> Recipe:
        """Recipe."""
        return self._recipe

    @property
    def returncode(self) -> int | None:
        """Return code of process."""
        return self._process.returncode

    @property
    def slurm_log(self) -> Path:
        """Path to Slurm log file."""
        return self._output_dir_slurm / f"{self.recipe.name}.log"

    @property
    def srun_executable(self) -> str:
        """`srun` executable."""
        return self._srun_executable

    @property
    def srun_options(self) -> dict[str, OptionValueType]:
        """Command line arguments for srun."""
        options: dict[str, OptionValueType] = {
            "--job-name": self.recipe.name,
            "--mpi": "cray_shasta",  # github.com/orgs/esmf-org/discussions/473
            "--ntasks": 1,
        }

        # Specify defaults if ICONEval is not run within sbatch script/salloc
        # session. Otherwise, do not specify anything here so that srun
        # automatically inherits the sbatch/salloc options. Always use just 1
        # task by default (we do not want to run recipes multiple times)
        if "SLURM_JOB_ACCOUNT" not in os.environ:
            options.update(
                {
                    "--cpus-per-task": 16,
                    "--mem-per-cpu": "1940M",
                    "--nodes": 1,
                    "--partition": "interactive",
                    "--time": "03:00:00",
                },
            )

        options.update(self._additional_srun_options)
        if not self._ignore_recipe_srun_options:
            options.update(self.recipe.template.srun_options)

        options["--account"] = self.account
        options["--output"] = str(self.slurm_log)
        options.pop("--error", None)  # stdout AND stderr should be in log

        return options

    def communicate(self) -> tuple[str, str]:
        """Communicate with process."""
        return self._process.communicate()

    def is_finished(self) -> bool:
        """Job has finished."""
        return self._process.poll() is not None

    def is_running(self) -> bool:
        """Job is running."""
        return self._process.poll() is None

    def is_successful(self) -> bool:
        """Job finished successful."""
        return self._process.poll() == 0

    def log_status(self) -> str:
        """Get status of job."""
        if self.is_running():
            return f"{self} is running"
        if self.is_successful():
            return f"<green>[+] {self} finished successfully</green>"
        return f"<red>[-] {self} failed with code {self.returncode}</red>"

    def start(self) -> None:
        """Start job."""
        srun_args = [f"{k}={v}" for (k, v) in self.srun_options.items()]
        esmvaltool_args = [f"{k}={v}" for (k, v) in self.esmvaltool_options.items()]
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(self.esmvaltool_config.dir)

        cmd: list[str] = [
            self.srun_executable,
            *srun_args,
            "--",
            self.esmvaltool_executable,
            "run",
            str(self.recipe.path),
            *esmvaltool_args,
        ]
        self._process = subprocess.Popen(  # noqa: S603
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            env=env,
        )

        logger.debug(
            f"  Ran '{' '.join(cmd)}' with ESMVALTOOL_CONFIG_DIR="
            f"'{self.esmvaltool_config.dir}'",
        )

    def terminate(self) -> None:
        """Terminate job."""
        self._process.terminate()
