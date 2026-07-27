from __future__ import annotations

import pytest

from tests.integration import OutputDirRegression


@pytest.fixture
def output_dir_regression(pytestconfig: pytest.Config) -> OutputDirRegression:
    return OutputDirRegression(
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )
