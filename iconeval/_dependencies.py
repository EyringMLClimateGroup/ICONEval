"""Module that manage dependencies of ICONEval."""

from __future__ import annotations

import subprocess

from loguru import logger

logger = logger.opt(colors=True)


def verify_esmvaltool_installation(esmvaltool_executable: str) -> None:
    """Check that esmvaltool is installed properly.

    Parameters
    ----------
    esmvaltool_executable:
        Path to ESMValTool executable.

    """
    logger.debug(
        f"Checking availability of ESMValTool using executable "
        f"'{esmvaltool_executable}'",
    )
    process = subprocess.run(  # noqa: S603
        ["which", esmvaltool_executable],  # noqa: S607
        shell=False,
        check=False,
        capture_output=True,
    )
    if process.returncode:
        msg = (
            f"{esmvaltool_executable} command not found, visit "
            f"https://docs.esmvaltool.org/en/latest/quickstart/"
            f"installation.html for ESMValTool installation instructions"
        )
        raise RuntimeError(msg)


def verify_slurm_installation(srun_executable: str) -> None:
    """Check that Slurm commands are available.

    Parameters
    ----------
    srun_executable:
        Path to `srun` executable.

    """
    logger.debug(
        f"Checking availability of Slurm Workload Manager using srun "
        f"executable '{srun_executable}'",
    )
    process = subprocess.run(  # noqa: S603
        ["which", srun_executable],  # noqa: S607
        shell=False,
        check=False,
        capture_output=True,
    )
    if process.returncode:
        msg = (
            f"{srun_executable} command not found, please make sure that the "
            f"Slurm Workload Manager is available on this machine"
        )
        raise RuntimeError(msg)
