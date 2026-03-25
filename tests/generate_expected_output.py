"""Generate expected output from tests."""

import tempfile
from pathlib import Path

import pytest

TESTS_ROOT = Path(__file__).parent


def main() -> None:
    """Generate expected output."""
    tmp_dir = tempfile.mkdtemp(
        prefix="expected_output_tmp_",
        dir=TESTS_ROOT,
    )

    pytest_args = [
        "-n0",
        "-m",
        "uses_expected_output",
        "--generate_expected_output",
        str(tmp_dir),
        str(TESTS_ROOT),
    ]
    pytest.main(pytest_args)

    original_output = TESTS_ROOT / "expected_output"
    print(f"Saved expected output to {tmp_dir}")  # noqa: T201
    print(  # noqa: T201
        f"Run `rm -rf {original_output} && mv {tmp_dir} {original_output}` to save it",
    )


if __name__ == "__main__":
    main()
