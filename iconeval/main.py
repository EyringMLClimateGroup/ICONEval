"""ICON model output evaluation with ESMValTool."""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import fire
from loguru import logger

import iconeval
from iconeval._dependencies import (
    verify_esmvaltool_installation,
    verify_slurm_installation,
)
from iconeval._logging import configure_logging
from iconeval._session import Session
from iconeval.output_handling._summarize import get_html_description, summarize
from iconeval.output_handling.publish_html import publish_esmvaltool_html

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

    from iconeval._job import Job
    from iconeval._typing import FacetType

logger = logger.opt(colors=True)

HEADER = r"""
------------------------------------------------
     ___ ____ ___  _   _ _____            _
    |_ _/ ___/ _ \| \ | | ____|_   ____ _| |
     | | |  | | | |  \| |  _| \ \ / / _` | |
     | | |__| |_| | |\  | |___ \ V / (_| | |
    |___\____\___/|_| \_|_____| \_/ \__,_|_|
------------------------------------------------
  ICON model output evaluation with ESMValTool
------------------------------------------------
"""
TIMES: dict[str, datetime] = {}


def icon_evaluation(
    *input_dirs: str | Path,
    publish_html: bool = False,
    html_name: str | None = None,
    recipe_templates: str | Path | Iterable[str | Path] | None = None,
    always_use_default_recipe_templates: bool = False,
    log_level: str = "info",
    log_file: str | Path | None = "~/.iconeval/debug.log",
    output_dir: str | Path | None = None,
    account: str | None = None,
    background: bool = False,
    dask: bool = True,
    esmvaltool_executable: str | Path = "esmvaltool",
    srun_executable: str | Path = "srun",
    ignore_recipe_esmvaltool_options: bool = False,
    ignore_recipe_srun_options: bool = False,
    ignore_recipe_dask_options: bool = False,
    esmvaltool_options: dict | None = None,
    srun_options: dict | None = None,
    dask_options: dict | None = None,
    tags: str | list[str] | None = None,
    setup_logging: bool = True,
    **extra_facets: FacetType,
) -> Path:
    """Evaluate ICON model output with ESMValTool.

    Specify a directory containing ICON simulation output and automatically run
    several (customizable) ESMValTool recipes on this output.

    Parameters
    ----------
    input_dirs:
        One or multiple ICON simulation directories that will be evaluated.
        These are the directories whose names are identical to the experiment
        name of the ICON simulation. E.g., `/root/to/my_amip_run` for the
        experiment with files `my_amip_run_lnd_mon_<date>.nc`.
    publish_html:
        Publish ESMValTool summary HTML on a **public** website using DKRZ's
        Python-swiftclient
        (https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html).
    html_name:
        Name that is used for the URL of the ESMValTool summary HTML and the
        output subdirectory that will be created in `output_dir`. Use this to
        get a consistent URL (this will potentially overwrite existing data!).
        If not given, use the (concatenated) experiment names of the input
        simulations including a datetime string.
    recipe_templates:
        Run the specified recipe templates. Unix-style wildcards are supported.
        To run multiple recipe (patterns), use the syntax
        `--recipe_templates='["/path/to/recipe_1.yml",
        "/path/to/recipe_2.yml"]'`. If `None`, run all default recipe templates
        available in the installation/repository directory of ICONEval. Make
        sure that all recipe template names start with `recipe_`.
    always_use_default_recipe_templates:
        If `True`, always run all default recipe templates available in the
        installation/repository directory of ICONEval in addition to the ones
        specified by `--recipe_templates`. If `False`, only run the recipes
        specified by `--recipe_templates`. If `--recipe_templates=None`, the
        default recipe templates will always be run.
    log_level:
        Log level. Must be one of `debug`, `info`, `warning`, `error`.
    log_file:
        File where ICONEval debug output is logged. If `None`, do not log to a
        file. New messages are attached to existing files.
    output_dir:
        Output directory where the output of ICONEval will be stored. If
        `None`, use the folder `output_iconeval` in the current working
        directory. If the directory does not exist yet, it will automatically
        be created. Output from individual ICONEval runs is not stored directly
        in the `--output_dir`, but rather in a subdirectory whose name is
        determined by the option `--html_name`.
    account:
        Account that is charged for the Slurm jobs. By default, use account
        that is used for `sbatch`/`salloc` (if ICONEval is run within `sbatch`
        script or `salloc` session), or `'bd1179'` otherwise.
    background:
        Terminate ICONEval after submitting all jobs/job steps. Summary HTMLs
        cannot be published/written in this mode.
    dask:
        If `True`, use Dask distributed scheduler when running ESMValTool. If
        `False`, use default (thread-based) Dask scheduler when running
        ESMValTool.
    esmvaltool_executable:
        Path to ESMValTool executable.
    srun_executable:
        Path to `srun` executable.
    ignore_recipe_esmvaltool_options:
        If `True`, ignore additional ESMValTool configuration options specified
        in the recipe templates via the syntax `#ESMVALTOOL --option=value`. If
        `False`, do not ignore them.srun_options
    ignore_recipe_srun_options:
        If `True`, ignore additional srun options specified in the recipe
        templates via the syntax `#SRUN --option=value`. If `False`, do not
        ignore them.
    ignore_recipe_dask_options:
        If `True`, ignore additional dask options specified in the recipe
        templates via the syntax `#DASK --option=value`. If `False`, do not
        ignore them.
    esmvaltool_options:
        Additional ESMValTool configuration options used to run all recipes.
        These settings will be overwritten by recipe-specific `#ESMVALTOOL`
        options. Use the syntax `--esmvaltool_options='{"--option":
        "value"}'`.
    srun_options:
        Additional srun options used to run all recipes. These settings will be
        overwritten by recipe-specific `#SRUN` options. Use the syntax
        `--srun_options='{"--option": "value"}'`.
    dask_options:
        Additional Dask options used to run all recipes. These settings will be
        overwritten by recipe-specific `#DASK` options. Ignored if
        `--dask=False`. Use the syntax `--dask_options='{"--option":
        "value"}'`.
    tags:
        Only recipes with the given tags are run (e.g., `--tags=tag`).  To not
        run specific recipes, use the syntax `!tag` (e.g., `--tags='!tag'`;
        make sure to properly escape the string via `'`).  Deselection takes
        priority over selection. If not given or empty, run all recipes. An
        overview of all available tags in the default recipe templates can be
        found here
        (https://github.com/EyringMLClimateGroup/ICONEval/blob/main/doc/tags.md).
        To specify multiple tags, use the syntax `'["tag1", "tag2", "!tag3"]'`.
    setup_logging:
        If `True`, set up new logging handlers; if `False`, skip that step
        (`log_level` and `log_file` are ignored in that case).
    **extra_facets:
        Additional options are considered as extra facets for the ICON data.
        All possible extra facets for ICON are given here
        (https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/
        find_data.html#icon).

    Returns
    -------
    :
        Output directory.

    Raises
    ------
    FileNotFoundError
        ``recipe_templates`` not found.
    NotADirectoryError
        ``input_dir`` not found.
    ValueError
        No input directory given.
    ValueError
        Invalid ``log_level`` is given.
    ValueError
        No recipes found to evaluate.
    ValueError
        An invalid template is given.

    """
    TIMES["start"] = datetime.now(UTC)

    # Initialize tool
    if setup_logging:
        configure_logging(log_level, log_file=log_file)
    logger.info("Starting ICONEval")
    logger.info(f"ICONEval version: {iconeval.__version__}")
    logger.info(f"Debug log: <cyan>{log_file}</cyan>")
    logger.info("")

    # Log all command line options
    logger.debug("Command line options:")
    logger.debug("---------------------")
    logger.debug(f"{'input_dirs':<35} = {input_dirs}")
    logger.debug(f"{'publish_html':<35} = {publish_html}")
    logger.debug(f"{'html_name':<35} = {html_name}")
    logger.debug(f"{'recipe_templates':<35} = {recipe_templates}")
    logger.debug(
        f"{'always_use_default_recipe_templates':<35} = "
        f"{always_use_default_recipe_templates}",
    )
    logger.debug(f"{'log_level':<35} = {log_level}")
    logger.debug(f"{'log_file':<35} = {log_file}")
    logger.debug(f"{'output_dir':<35} = {output_dir}")
    logger.debug(f"{'account':<35} = {account}")
    logger.debug(f"{'background':<35} = {background}")
    logger.debug(f"{'dask':<35} = {dask}")
    logger.debug(f"{'esmvaltool_executable':<35} = {esmvaltool_executable}")
    logger.debug(f"{'srun_executable':<35} = {srun_executable}")
    logger.debug(f"{'tags':<35} = {tags}")
    logger.debug(
        f"{'ignore_recipe_esmvaltool_options':<35} = "
        f"{ignore_recipe_esmvaltool_options}",
    )
    logger.debug(
        f"{'ignore_recipe_srun_options':<35} = {ignore_recipe_srun_options}",
    )
    logger.debug(
        f"{'ignore_recipe_dask_options':<35} = {ignore_recipe_dask_options}",
    )
    logger.debug(f"{'esmvaltool_options':<35} = {esmvaltool_options}")
    logger.debug(f"{'srun_options':<35} = {srun_options}")
    logger.debug(f"{'dask_options':<35} = {dask_options}")
    if extra_facets:
        logger.debug("Extra facets:")
        for key, val in extra_facets.items():
            logger.debug(f"  {key} = {val}")
    logger.debug("")

    # Verify that all dependencies are available
    esmvaltool_executable = str(esmvaltool_executable)
    srun_executable = str(srun_executable)
    verify_esmvaltool_installation(esmvaltool_executable)
    verify_slurm_installation(srun_executable)
    logger.debug("")

    # Get default account if necessary
    if account is None:
        if "SLURM_JOB_ACCOUNT" in os.environ:
            account = os.environ["SLURM_JOB_ACCOUNT"]
        else:
            account = "bd1179"

    # Basic setup of IO directories and files
    TIMES["start_setup"] = datetime.now(UTC)
    session = Session(input_dirs, output_dir, html_name)
    TIMES["end_setup"] = datetime.now(UTC)

    # Setup jobs (i.e., recipes and configuration)
    jobs = session.get_jobs(
        recipe_template_paths=recipe_templates,
        always_use_default_recipe_templates=always_use_default_recipe_templates,
        account=account,
        dask=dask,
        esmvaltool_executable=esmvaltool_executable,
        srun_executable=srun_executable,
        ignore_recipe_esmvaltool_options=ignore_recipe_esmvaltool_options,
        ignore_recipe_srun_options=ignore_recipe_srun_options,
        ignore_recipe_dask_options=ignore_recipe_dask_options,
        additional_esmvaltool_options=esmvaltool_options,
        additional_srun_options=srun_options,
        additional_dask_options=dask_options,
        tags=tags,
        **extra_facets,
    )
    logger.debug("Recipes:")
    logger.debug("--------")
    for job in jobs:
        logger.debug(f"  - {job.recipe.path}")
    logger.debug("")

    # Run jobs
    _run_jobs(jobs, background=background)
    if background:
        TIMES["end"] = datetime.now(UTC)
        logger.info("Ending ICONEval")
        logger.info(
            f"Time for running ICONEval was {TIMES['end'] - TIMES['start']}",
        )
        return session.output_dir

    # Create summary HTML and publish it if desired
    TIMES["start_html"] = datetime.now(UTC)
    logger.info("HTML output:")
    logger.info("------------")
    _create_summary_html(session)
    if publish_html:
        _publish_html(session, html_name)
    TIMES["end_html"] = datetime.now(UTC)
    logger.debug(
        f"Time for creating HTML output was {TIMES['end_html'] - TIMES['start_html']}",
    )
    logger.info("")

    # Print summary
    TIMES["end"] = datetime.now(UTC)
    logger.info("Ending ICONEval")
    logger.info(
        f"Time for running ICONEval was {TIMES['end'] - TIMES['start']}",
    )

    return session.output_dir


def _create_summary_html(session: Session) -> None:
    """Create summary HTML."""
    description = get_html_description(session, TIMES["start"])
    summarize(session.output_dir_esmvaltool, description=description)


def _publish_html(
    session: Session,
    html_name: str | None,
) -> None:
    """Publish HTML."""
    if html_name is None:
        html_name = session.output_dir.name
    container_name = "iconeval"
    logger.info(
        f"Publishing results in swift container '{container_name}' under "
        f"directory '{html_name}'",
    )
    publish_esmvaltool_html(
        session.output_dir_esmvaltool,
        container_name=container_name,
        dir_name=html_name,
        setup_logging=False,
    )


def _run_jobs(jobs: Sequence[Job], *, background: bool) -> None:
    """Run all jobs."""
    TIMES["start_jobs"] = datetime.now(UTC)
    logger.info("Jobs:")
    logger.info("-----")

    # Start jobs
    for job in jobs:
        logger.info(f"- <magenta>{job}</magenta> (Log: <cyan>{job.slurm_log}</cyan>)")
        job.start()
    logger.info("")
    n_jobs = len(jobs)
    run_jobs_msg = f"Running {n_jobs} job(s):"
    logger.info(run_jobs_msg)
    logger.info("-" * len(run_jobs_msg))

    # Run jobs in background
    if background:
        TIMES["end_jobs"] = datetime.now(UTC)
        logger.info(f"All {n_jobs} job(s) are running in background now")
        logger.debug(
            f"Time for starting the job(s) was "
            f"{TIMES['end_jobs'] - TIMES['start_jobs']}",
        )
        logger.info("")
        return

    # Run jobs in foreground
    successful_jobs = []
    finished_jobs = []
    try:
        while True:
            for job in jobs:
                if job.is_running():
                    continue
                if job in finished_jobs:
                    continue
                logger.info(f"{job.log_status()}")
                logger.info(f"    Log: <cyan>{job.slurm_log}</cyan>")
                (stdout, stderr) = job.communicate()
                logger.debug("    Output to stdout:")
                logger.debug(stdout)
                logger.debug("    Output to stderr:")
                logger.debug(stderr)
                if job.is_successful():
                    successful_jobs.append(job)
                finished_jobs.append(job)
                n_running_jobs = n_jobs - len(finished_jobs)
                if n_running_jobs:
                    logger.info(
                        f"    {n_running_jobs}/{n_jobs} job(s) are still running",
                    )
            time.sleep(1.0)
            if len(finished_jobs) == n_jobs:
                break

    # Always terminate jobs when exiting the loop
    finally:
        logger.debug("Terminating all running jobs")
        for job in jobs:
            if job.is_running():
                job.terminate()
                logger.debug(f"  - Terminated {job}")

    TIMES["end_jobs"] = datetime.now(UTC)
    logger.info(
        f"{len(successful_jobs)}/{n_jobs} job(s) finished successfully",
    )
    logger.debug(
        f"Time for running the job(s) was {TIMES['end_jobs'] - TIMES['start_jobs']}",
    )
    logger.info("")

    return


def main() -> None:
    """Invoke ``fire`` to process command line arguments."""
    logger.remove()  # remove any potential handlers
    print(HEADER)  # noqa: T201
    fire.Fire(icon_evaluation)


if __name__ == "__main__":  # pragma: no cover
    main()
