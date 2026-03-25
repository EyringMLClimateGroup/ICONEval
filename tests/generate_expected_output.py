"""Generate expected output from tests."""

import tempfile
from pathlib import Path

import pytest

TESTS_ROOT = Path(__file__).parent


def main() -> None:
    """Generate expected output."""
    temp_dir = tempfile.mkdtemp(
        prefix="expected_output_tmp_",
        dir=TESTS_ROOT,
    )

    pytest_args = [
        "-n0",
        "-m",
        "uses_expected_output",
        "--generate_expected_output",
        str(temp_dir),
        str(TESTS_ROOT),
    ]
    pytest.main(pytest_args)

    print("Saved expected output to", temp_dir)  # noqa: T201


if __name__ == "__main__":
    main()
