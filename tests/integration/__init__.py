from __future__ import annotations

import filecmp
from pprint import pformat
import re
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from pytest_datadir.plugin import LazyDataDir

TMP_PATH_PLACEHOLDER = "((tmp_path))"


class OutputDirRegression:
    def __init__(self, original_datadir: Path, request: pytest.FixtureRequest) -> None:
        """Initialize class instance."""
        subdir = re.sub(r"[\W]", "_", request.node.name)
        self.expected_dir = original_datadir / subdir
        self.request = request

    def check(self, obtained_dir: Path, empty_subdirs: list[str] | None = None) -> None:
        """Check if files and directories written by code match expected output."""
        if empty_subdirs is None:
            empty_subdirs = []

        regen_output = (
            not self.expected_dir.is_dir() or
            self.request.config.getoption("force_regen") or
            self.request.config.getoption("regen_all")
        )
        if regen_output:
            shutil.rmtree(self.expected_dir, ignore_errors=True)
            shutil.copytree(obtained_dir, self.expected_dir)

            # Empty directories cannot be checked out on git, so we simply
            # delete them here
            subdirs = (d for d in self.expected_dir.iterdir() if d.is_dir())
            for subdir in subdirs:
                if not list(subdir.iterdir()):
                    subdir.rmdir()

            if not self.request.config.getoption("regen_all"):
                if self.request.config.getoption("force_regen"):
                    msg = (
                        f"--force-regen set, regenerating expected output "
                        f"directory at: {self.expected_dir}"
                    )
                else:
                    msg = (
                        f"Expected output directory not found, created "
                        f"{self.expected_dir}"
                    )
                pytest.fail(msg)

            # Replace temporary directory with placeholder
            # for _root, _, _files in target_dir.walk():
            #     for _file in _files:
            #         file_path = _root / _file
            #         content = file_path.read_text(encoding="utf-8")
            #         content = content.replace(str(tmp_path), TMP_PATH_PLACEHOLDER)
            #         file_path.write_text(content, encoding="utf-8")

            return

        # Empty directories cannot be checked out on git, so we need to account
        # for this here
        for empty_dir in empty_subdirs:
            empty_path = obtained_dir / empty_dir
            msg = f"Assumed empty directory {empty_dir} is not a directory"
            assert empty_path.is_dir(), msg
            msg = f"Assumed empty directory {empty_dir} is not empty"
            assert len(list(empty_path.iterdir())) == 0, msg
            empty_path.rmdir()

        # Check that all files and directories are identical
        for _root, _dirs, _files in self.expected_dir.walk():
            obtained_root = obtained_dir / _root.relative_to(self.expected_dir)
            obtained_objects = [o.name for o in obtained_root.iterdir()]
            expected_objects = _dirs + _files
            msg = (
                f"Expected {len(expected_objects)} objects in directory {_root}:\n"
                f"{pformat(expected_objects)}\nGot {len(obtained_objects)}:\n"
                f"{pformat(obtained_objects)}"
            )
            assert len(obtained_objects) == len(expected_objects), msg
            for _dir in _dirs:
                obtained_subdir = obtained_root / _dir
                actual_dir = obtained_dir / obtained_subdir
                msg = f"Expected directory {obtained_subdir} does not exist"
                assert actual_dir.is_dir(), msg
            for _file in _files:
                obtained_file = obtained_root / _file
                actual_file = obtained_dir / obtained_file
                expected_file = _root / _file
                msg = f"Expected file {obtained_file} does not exist"
                assert actual_file.is_file(), msg
                msg = (
                    f"Obtained file {actual_file} does not not match expected "
                    f"file {expected_file}"
                )
                assert filecmp.cmp(actual_file, expected_file, shallow=False), msg

                # Replace placeholders
                # actual_content = actual_file.read_text(encoding="utf-8")
                # # actual_content = actual_content.replace(str(tmp_path), TMP_PATH_PLACEHOLDER)
                # expected_content = expected_file.read_text(encoding="utf-8")

                # # Compare YAML files by actually parsing them
                # if expected_file.suffix in (".yml", ".yaml"):
                #     actual_content = yaml.safe_load(actual_content)
                #     expected_content = yaml.safe_load(expected_content)

                # # Compare files
                # assert actual_content == expected_content



@contextmanager
def copy_to_tmp_path(tmp_path: Path, dir_to_copy: Path) -> Generator[Path]:
    """Copy contents of a directory to temporary location and remove them afterwards."""
    original_contents = [obj.name for obj in dir_to_copy.iterdir()]
    tmp_dir = tmp_path / dir_to_copy.name
    shutil.copytree(dir_to_copy, tmp_dir)

    yield tmp_dir

    for obj in original_contents:
        obj_path = tmp_dir / obj
        if obj_path.is_file():
            obj_path.unlink()
        elif obj_path.is_dir():
            shutil.rmtree(obj_path)
