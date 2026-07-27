from __future__ import annotations

import filecmp
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

TMP_PATH_PLACEHOLDER = "((tmp_path))"


class OutputDirRegression:
    def __init__(self, *, generate_expected_output: str | None = None) -> None:
        """Initialize class instance."""
        self.generate_expected_output = generate_expected_output

    def check(
        self,
        actual_output: Path,
        expected_output: Path,
        empty_dirs: list[str] | None = None,
        ignore_top_level_files_and_dirs: Iterable[Path] | None = None,
    ) -> None:
        """Check if files and directories written by code match expected output."""
        if empty_dirs is None:
            empty_dirs = []
        if ignore_top_level_files_and_dirs is None:
            ignore_top_level_files_and_dirs = []

        # If desired, write expected output instead of checking it
        if self.generate_expected_output is not None:
            target_dir = (
                Path(self.generate_expected_output).resolve() / expected_output.name
            )
            if target_dir.is_dir():
                msg = f"Directory {target_dir} already exists"
                raise FileExistsError(msg)
            target_dir.mkdir(parents=True, exist_ok=True)
            for obj in actual_output.iterdir():
                # if obj.name in ignore_top_level_files_and_dirs:
                #     continue
                if obj.is_dir():
                    shutil.copytree(obj, target_dir / obj.name)
                else:
                    shutil.copy2(obj, target_dir)

            # Delete empty directories (those cannot be checkout out on git)
            subdirs = (d for d in target_dir.iterdir() if d.is_dir())
            for subdir in subdirs:
                if not list(subdir.iterdir()):
                    subdir.rmdir()

            # Replace temporary directory with placeholder
            # for _root, _, _files in target_dir.walk():
            #     for _file in _files:
            #         file_path = _root / _file
            #         content = file_path.read_text(encoding="utf-8")
            #         content = content.replace(str(tmp_path), TMP_PATH_PLACEHOLDER)
            #         file_path.write_text(content, encoding="utf-8")

            return

        # Empty directories cannot be checked out on git, so we need to account for
        # this here
        for empty_dir in empty_dirs:
            empty_path = actual_output / empty_dir
            assert empty_path.is_dir()
            assert len(list(empty_path.iterdir())) == 0
            empty_path.rmdir()

        # Check that all files and directories are identical
        for _root, _dirs, _files in expected_output.walk():
            relative_actual_output = actual_output / _root.relative_to(expected_output)
            n_objects = len(_dirs) + len(_files)
            assert len(list(relative_actual_output.iterdir())) == n_objects
            for _dir in _dirs:
                actual_dir = actual_output / relative_actual_output / _dir
                msg = f"Directory {actual_dir} does not exist"
                assert actual_dir.is_dir(), msg
            for _file in _files:
                actual_file = actual_output / relative_actual_output / _file
                expected_file = _root / _file
                msg = f"File {actual_file} does not exist"
                assert actual_file.is_file(), msg
                msg = (
                    f"File {actual_file} does not not match expected file "
                    f"{expected_file}"
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
