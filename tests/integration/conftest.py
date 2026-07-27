from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration import OutputDirRegression

if TYPE_CHECKING:
    from pathlib import Path



@pytest.fixture
def output_dir_regression(
    original_datadir: Path,
    request: pytest.FixtureRequest,
) -> OutputDirRegression:
    return OutputDirRegression(original_datadir, request)
