from __future__ import annotations

import shutil
from pathlib import Path

import yaml

TMP_PATH_PLACEHOLDER = "((tmp_path))"


def assert_output(
    tmp_path: Path,
    actual_output: Path,
    expected_output: Path,
    empty_dirs: list[str] | None = None,
    generate_expected_output: str | None = None,
) -> None:
    # If desired, write expected output instead of checking it
    if generate_expected_output is not None:
        target_dir = Path(generate_expected_output).resolve() / expected_output.name
        try:
            shutil.copytree(actual_output, target_dir)
        except FileExistsError:
            return

        # Delete empty directories (those cannot be checkout out on git)
        subdirs = (d for d in target_dir.iterdir() if d.is_dir())
        for subdir in subdirs:
            if not list(subdir.iterdir()):
                subdir.rmdir()

        # Replace temporary directory with placeholder
        for _root, _, _files in target_dir.walk():
            for _file in _files:
                file_path = _root / _file
                content = file_path.read_text(encoding="utf-8")
                content = content.replace(str(tmp_path), TMP_PATH_PLACEHOLDER)
                file_path.write_text(content, encoding="utf-8")

        return

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

            # Replace placeholders
            actual_content = actual_file.read_text(encoding="utf-8")
            actual_content = actual_content.replace(str(tmp_path), TMP_PATH_PLACEHOLDER)
            expected_content = expected_file.read_text(encoding="utf-8")

            # Compare YAML files by actually parsing them
            if expected_file.suffix in (".yml", ".yaml"):
                actual_content = yaml.safe_load(actual_content)
                expected_content = yaml.safe_load(expected_content)

            # Compare files
            assert actual_content == expected_content
