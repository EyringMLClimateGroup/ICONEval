from __future__ import annotations

import builtins
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from loguru import logger

import iconeval._io_handler
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
    # datetime
    modules = [
        iconeval._io_handler,
        iconeval._simulation_info,
        iconeval.main,
        iconeval.output_handling._summarize,
        iconeval.output_handling.publish_html,
    ]
    for module in modules:
        mock = mocker.patch.object(module, "datetime", autospec=True)
        mock.now.return_value = datetime(2000, 1, 1, 0, 0, 0)
        mock.fromtimestamp.return_value = datetime(2000, 1, 1, 0, 0, 0)
        mock.strptime = datetime.strptime

    # time
    modules = [iconeval.main, iconeval.output_handling.publish_html]
    for module in modules:
        mock = mocker.patch.object(module, "time", autospec=True)
        mock.tzname = ["NOT_MY_TIMEZONE", "MY_TIMEZONE"]
        mock.time.return_value = 0


@pytest.fixture(autouse=True)
def fix_user(mocker: MockerFixture) -> None:
    modules = [
        iconeval._simulation_info,
        iconeval.output_handling._summarize,
    ]
    for module in modules:
        mocker.patch.object(
            module,
            "get_user_name",
            autospec=True,
            return_value="ICONEval User",
        )


@pytest.fixture(autouse=True)
def fix_user_input(mocker: MockerFixture) -> None:
    mocker.patch.object(
        builtins,
        "input",
        autospec=True,
        return_value="user input",
    )
    mocker.patch.object(
        iconeval.output_handling.publish_html,
        "getpass",
        autospec=True,
        return_value="super secret password",
    )


@pytest.fixture(autouse=True)
def mocked_swift_head_account(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(
        iconeval.output_handling.publish_html,
        "head_account",
        autospec=True,
    )


@pytest.fixture(autouse=True)
def mocked_requests(mocker: MockerFixture) -> Mock:
    mock = mocker.patch.object(
        iconeval.output_handling.publish_html,
        "requests",
        autospec=True,
        return_value="super secret password",
    )
    mock.get.return_value.headers = {
        "x-auth-token": "my x-auth-token",
        "x-storage-url": "my x-storage-url",
        "x-auth-token-expires": "42",
    }
    return mock


@pytest.fixture(autouse=True)
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
    """Remove all potential logging handlers before running any test."""
    logger.remove()


@pytest.fixture
def sample_data_path() -> Path:
    return Path(str(files("tests"))).resolve() / "sample_data"


@pytest.fixture(autouse=True)
def use_custom_swiftenv(
    monkeypatch: pytest.MonkeyPatch,
    sample_data_path: Path,
) -> None:
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "SWIFT_BASE",
        "url/to/swift_storage/",
    )
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "SWIFTENV",
        sample_data_path / "swift" / "swiftenv",
    )
