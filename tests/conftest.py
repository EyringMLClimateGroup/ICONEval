from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import sentinel

import pytest

import iconeval._dependencies
import iconeval._job

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

pytest.register_assert_rewrite("tests.integration")


@pytest.fixture
def expected_output_dir() -> Path:
    return Path(str(files("tests"))).resolve() / "expected_output"


@pytest.fixture
def mocked_subprocess__dependencies(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._dependencies, "subprocess", autospec=True)
    mock.run.return_value.returncode = 0
    return mock


@pytest.fixture
def mocked_subprocess__job(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._job, "subprocess", autospec=True)
    mock.Popen.return_value.poll.return_value = 0
    mock.Popen.return_value.communicate.return_value = ("stdout", "stderr")
    mock.PIPE = sentinel.PIPE
    return mock


@pytest.fixture
def sample_data_path() -> Path:
    return Path(str(files("tests"))).resolve() / "sample_data"
