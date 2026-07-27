from __future__ import annotations

import filecmp
import re
import shutil
from pprint import pformat
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

TMP_PATH_PLACEHOLDER = "((tmp_path))"


class OutputDirRegression:
    def __init__(self, original_datadir: Path, request: pytest.FixtureRequest) -> None:
        """Initialize class instance."""
        subdir = re.sub(r"[\W]", "_", request.node.name)
        self.expected_dir = original_datadir / subdir
        self.request = request

    def check(
        self,
        obtained_dir: Path,
        *,
        empty_subdirs: list[str] | None = None,
    ) -> None:
        """Check if files and directories written by code match expected output."""
        if empty_subdirs is None:
            empty_subdirs = []

        # `obtained_dir` is usually a temporary pytest path. If obtained text
        # files contain these temporary pytest paths, this will lead to test
        # failures. Thus, text files need to be sanitized before saving them.
        # Note: temporary pytest paths are of the form
        # /tmp/pytest-of-{user}/pytest-{run_number}/test_{name-of-test}...
        parent_dirs_that_start_with_test_ = [
            p for p in obtained_dir.parents if str(p.name).startswith("test_")
        ]
        tmp_path = (
            None
            if not parent_dirs_that_start_with_test_
            else str(parent_dirs_that_start_with_test_[-1])
        )

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

            # Sanitize text files
            if tmp_path is not None:
                for root, _, files in self.expected_dir.walk():
                    for file in files:
                        self._sanitize_file(root / file, tmp_path)

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
        for root, dirs, files in self.expected_dir.walk():
            obtained_root = obtained_dir / root.relative_to(self.expected_dir)
            obtained_objects = [o.name for o in obtained_root.iterdir()]
            expected_objects = dirs + files
            msg = (
                f"Expected {len(expected_objects)} objects in directory "
                f"{obtained_root}:\n{pformat(expected_objects)}\n"
                f"Got {len(obtained_objects)}:\n{pformat(obtained_objects)}"
            )
            assert len(obtained_objects) == len(expected_objects), msg
            for dir_ in dirs:
                obtained_subdir = obtained_root / dir_
                msg = f"Expected directory {obtained_subdir} does not exist"
                assert obtained_subdir.is_dir(), msg
            for file in files:
                obtained_file = obtained_root / file
                expected_file = root / file
                msg = f"Expected file {obtained_file} does not exist"
                if tmp_path is not None:
                    self._sanitize_file(obtained_file, tmp_path)
                assert obtained_file.is_file(), msg
                msg = (
                    f"Obtained file {obtained_file} does not not match expected "
                    f"file {expected_file}"
                )
                assert filecmp.cmp(obtained_file, expected_file, shallow=False), msg
                msg = (
                    f"Permissions of obtained file {obtained_file} "
                    f"({oct(obtained_file.stat().st_mode)}) do not not match "
                    f"permissions of expected file {expected_file} "
                    f"({oct(expected_file.stat().st_mode)})"
                )
                assert obtained_file.stat().st_mode == expected_file.stat().st_mode, msg

    def _sanitize_file(self, file: Path, tmp_path: str) -> None:
        """Sanitize file (in-place)."""
        content = file.read_text(encoding="utf-8")
        content = content.replace(tmp_path, TMP_PATH_PLACEHOLDER)
        file.write_text(content, encoding="utf-8")
