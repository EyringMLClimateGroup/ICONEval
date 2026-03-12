from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import yaml

if TYPE_CHECKING:
    from pathlib import Path


def assert_output(
    input_dirs: list[Path],
    actual_output: Path,
    expected_output: Path,
    empty_dirs: list[str] | None = None,
) -> None:
    # Empty directories cannot be checked out on git, so we need to account for
    # this here
    if empty_dirs is None:
        empty_dirs = []
    for empty_dir in empty_dirs:
        empty_path = actual_output / empty_dir
        assert empty_path.is_dir()
        assert len(list(empty_path.iterdir())) == 0
        empty_path.rmdir()

    # Check that all files and directories exist
    for _root, _dirs, _files in expected_output.walk():
        relative_actual_output = actual_output / _root.relative_to(expected_output)
        n_objects = len(_dirs) + len(_files)
        assert len(list(relative_actual_output.iterdir())) == n_objects
        for _dir in _dirs:
            actual_dir = actual_output / relative_actual_output / _dir
            assert actual_dir.is_dir()
        for _file in _files:
            actual_file = actual_output / relative_actual_output / _file
            expected_file = _root / _file
            assert actual_file.is_file()

            # Recipes and debug.html are expected to be identical
            if expected_file.name.startswith("recipe_"):
                with actual_file.open(encoding="utf-8") as file:
                    actual_content = yaml.safe_load(file)
                with expected_file.open(encoding="utf-8") as file:
                    expected_content = yaml.safe_load(file)
                assert actual_content == expected_content
            elif expected_file.name == "debug.html":
                actual_content = actual_file.read_text(encoding="utf-8")
                expected_content = expected_file.read_text(encoding="utf-8")
                assert actual_content == expected_content

            # Config files are different (different paths), so we need to be
            # more careful here
            elif expected_file.name == "config-user.yml":
                with actual_file.open(encoding="utf-8") as file:
                    actual_content = yaml.safe_load(file)
                with expected_file.open(encoding="utf-8") as file:
                    expected_content = yaml.safe_load(file)
                assert actual_content.keys() == expected_content.keys()
                identical_keys = ["auxiliary_data_dir", "dask", "max_parallel_tasks"]
                for key in identical_keys:
                    assert actual_content[key] == expected_content[key]
                assert actual_content["output_dir"] == str(
                    actual_output / "esmvaltool_output",
                )

                # Projects
                assert (
                    actual_content["projects"].keys()
                    == expected_content["projects"].keys()
                )
                identical_projects = [
                    "CMIP6",
                    "CMIP5",
                    "CMIP3",
                    "CORDEX",
                    "obs4MIPs",
                    "ana4MIPs",
                    "native6",
                    "OBS6",
                    "OBS",
                ]
                for project in identical_projects:
                    assert (
                        actual_content["projects"][project]
                        == expected_content["projects"][project]
                    )

                # ICON
                expected_icon_config: dict[str, dict[str, str]] = {}
                for input_dir in input_dirs:
                    icon_config = {
                        "filename_template": "{exp}_{var_type}*.nc",
                        "rootpath": str(input_dir),
                        "type": "esmvalcore.io.local.LocalDataSource",
                    }
                    exp = input_dir.stem
                    expected_icon_config[exp] = {
                        **icon_config,
                        "dirname_template": "",
                    }
                    expected_icon_config[f"{exp}-outdata"] = {
                        **icon_config,
                        "dirname_template": "outdata",
                    }
                    expected_icon_config[f"{exp}-output"] = {
                        **icon_config,
                        "dirname_template": "output",
                    }
                assert actual_content["projects"]["ICON"] == {
                    "data": expected_icon_config,
                }

                # EMAC
                expected_emac_config: dict[str, dict[str, Any]] = {}
                for input_dir in input_dirs:
                    exp = input_dir.stem
                    expected_emac_config[exp] = {
                        "dirname_template": "{channel}",
                        "filename_template": "{exp}*{channel}{postproc_flag}.nc",
                        "ignore_warnings": [
                            {
                                "message": "Ignored formula of unrecognised type: .*",
                                "module": "iris",
                            },
                            {
                                "message": "Ignoring formula terms variable .* "
                                "referenced by data variable .* via "
                                "variable .*",
                                "module": "iris",
                            },
                            {
                                "message": "Missing CF-netCDF formula term variable "
                                ".*, referenced by netCDF variable .*",
                                "module": "iris",
                            },
                            {
                                "message": "NetCDF variable .* contains unknown "
                                "cell method .*",
                                "module": "iris",
                            },
                        ],
                        "rootpath": str(input_dir),
                        "type": "esmvalcore.io.local.LocalDataSource",
                    }
                assert actual_content["projects"]["EMAC"] == {
                    "data": expected_emac_config,
                }

            # For index.html files, just check that basic information is
            # present
            elif expected_file.name.startswith("index"):
                actual_content = actual_file.read_text(encoding="utf-8")
                for input_dir in input_dirs:
                    assert f"Path: {input_dir}" in actual_content

            else:
                pytest.fail(f"Unknown file type in output ({_file})")
