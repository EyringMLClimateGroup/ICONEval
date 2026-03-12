from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import call, sentinel

from iconeval.main import icon_evaluation
from tests.integration import assert_output

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import Mock


def test_icon_evaluation_single_input(
    expected_output_dir: Path,
    tmp_path: Path,
    mocked_subprocess__dependencies: Mock,
    mocked_subprocess__job: Mock,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_output = icon_evaluation(input_dir, output_dir=output_dir, log_file=None)

    # Check output
    expected_output = expected_output_dir / "test_icon_evaluation_single_input"
    assert_output(
        [input_dir],
        actual_output,
        expected_output,
        empty_dirs=["pdfs", "slurm"],
    )

    # Check mock calls
    assert mocked_subprocess__dependencies.run.mock_calls == [
        call(
            ["which", "esmvaltool"],
            shell=False,
            check=False,
            capture_output=True,
        ),
        call(
            ["which", "srun"],
            shell=False,
            check=False,
            capture_output=True,
        ),
    ]

    recipes = list((expected_output / "recipes").glob("*.yml"))
    assert mocked_subprocess__job.Popen.call_count == len(recipes)
    assert mocked_subprocess__job.Popen.return_value.communicate.call_count == len(
        recipes,
    )
    for recipe in recipes:
        cmd = [
            "srun",
            f"--job-name={recipe.stem}",
            "--mpi=cray_shasta",
            "--ntasks=1",
            "--cpus-per-task=16",
            "--mem-per-cpu=1940M",
            "--nodes=1",
            "--partition=interactive",
            "--time=03:00:00",
            "--account=bd1179",
            f"--output={actual_output / 'slurm' / f'{recipe.stem}.log'}",
            "--",
            "esmvaltool",
            "run",
            str(actual_output / "recipes" / recipe.name),
        ]
        if "portrait_plot" in recipe.stem:
            cmd.append("--max_parallel_tasks=1")
        env = dict(os.environ)
        env["ESMVALTOOL_USE_NEW_DASK_CONFIG"] = "TRUE"
        env["ESMVALTOOL_CONFIG_DIR"] = str(actual_output / "config" / recipe.stem)
        mocked_subprocess__job.Popen.assert_any_call(
            cmd,
            shell=False,
            stdout=sentinel.PIPE,
            stderr=sentinel.PIPE,
            encoding="utf-8",
            env=env,
        )
