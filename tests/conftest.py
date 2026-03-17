from __future__ import annotations

from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import sentinel

import pytest
from loguru import logger

import iconeval._dependencies
import iconeval._job
import iconeval._simulation_info
import iconeval.main
import iconeval.output_handling._summarize
import iconeval.output_handling.publish_html

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

pytest.register_assert_rewrite("tests.integration")

logger = logger.opt(colors=True)


@pytest.fixture(autouse=True)
def always_ignore_swift_token(mocker: MockerFixture) -> None:
    mocker.patch.object(
        iconeval.output_handling.publish_html,
        "_valid_swift_token_available",
        autospec=True,
        return_value=False,
    )
    mocker.patch.object(
        iconeval.output_handling.publish_html,
        "_create_swift_token",
        autospec=True,
        return_value=None,
    )
    mocker.patch.object(
        iconeval.output_handling.publish_html,
        "_read_swiftenv",
        autospec=True,
        return_value=("token", "url", datetime(2000, 1, 1, 0, 0, 0)),
    )


@pytest.fixture
def caplog(caplog: pytest.LogCaptureFixture) -> Generator[pytest.LogCaptureFixture]:
    """Overwrite default caplog feature so it works with loguru."""
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,
    )
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def expected_output_dir() -> Path:
    return Path(str(files("tests"))).resolve() / "expected_output"


@pytest.fixture(autouse=True)
def fix_time(mocker: MockerFixture) -> None:
    mock = mocker.patch.object(iconeval.main, "datetime", autospec=True)
    mock.now.return_value = datetime(2000, 1, 1, 0, 0, 0)
    mock = mocker.patch.object(iconeval._io_handler, "datetime", autospec=True)
    mock.now.return_value = datetime(2000, 1, 1, 0, 0, 0)
    mock = mocker.patch.object(iconeval._simulation_info, "datetime", autospec=True)
    mock.fromtimestamp.return_value = datetime(2000, 1, 1, 0, 0, 0)
    mock = mocker.patch.object(
        iconeval.output_handling.publish_html,
        "datetime",
        autospec=True,
    )
    mock.fromtimestamp.return_value = datetime(2000, 1, 1, 0, 0, 0)


@pytest.fixture(autouse=True)
def fix_user(mocker: MockerFixture) -> None:
    mocker.patch.object(
        iconeval._simulation_info,
        "get_user_name",
        autospec=True,
        return_value="ICONEval User",
    )
    mocker.patch.object(
        iconeval.output_handling._summarize,
        "get_user_name",
        autospec=True,
        return_value="ICONEval User",
    )


@pytest.fixture
def mocked_plots2pdf(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(iconeval.main, "plots2pdf", autospec=True)


@pytest.fixture
def mocked_subprocess__dependencies(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._dependencies, "subprocess", autospec=True)
    mock.run.return_value.returncode = 0
    return mock


@pytest.fixture
def mocked_subprocess__job(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(iconeval._job, "subprocess", autospec=True)
    mock.Popen.return_value.returncode = 0
    mock.Popen.return_value.poll.return_value = 0
    mock.Popen.return_value.communicate.return_value = ("stdout", "stderr")
    mock.PIPE = sentinel.PIPE
    return mock


@pytest.fixture
def mocked_swift_service(mocker: MockerFixture) -> Mock:
    mocked_upload_object = mocker.patch.object(
        iconeval.output_handling.publish_html,
        "SwiftUploadObject",
        autospec=True,
    )
    mocked_upload_object.side_effect = lambda f, object_name=None: (f, object_name)

    return mocker.patch.object(
        iconeval.output_handling.publish_html,
        "SwiftService",
        autospec=True,
    )


@pytest.fixture
def recipe_template_dir() -> Path:
    return Path(str(files("iconeval"))).resolve() / "recipe_templates"


@pytest.fixture(autouse=True)
def remove_default_logger_handlers() -> None:
    """Remove all potential logging handlers."""
    logger.remove()


@pytest.fixture
def sample_data_path() -> Path:
    return Path(str(files("tests"))).resolve() / "sample_data"
