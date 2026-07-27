from __future__ import annotations

import builtins
import locale
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
import requests
from loguru import logger

import iconeval._session
import iconeval._simulation_info
import iconeval.main
import iconeval.output_handling._summarize
import iconeval.output_handling.publish_html
from iconeval._logging import _add_console_handler

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import Mock

    from pytest_datadir.plugin import LazyDataDir
    from pytest_mock import MockerFixture

pytest.register_assert_rewrite("tests.integration")

logger = logger.opt(colors=True)


# Pytest configuration


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add pytest options."""
    # Similar to https://github.com/ESSS/pytest-regressions
    parser.addoption(
        "--force-regen",
        action="store_true",
        default=False,
        help="Regenerate regression data files, failing tests with different data.",
    )
    parser.addoption(
        "--regen-all",
        action="store_true",
        default=False,
        help=(
            "Regenerate all files, letting tests pass (use to regenerate "
            "everything in one run)."
        ),
    )


# Automatically used fixtures


@pytest.fixture(autouse=True)
def fix_locale() -> None:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


@pytest.fixture(autouse=True)
def fix_time(mocker: MockerFixture) -> None:
    # datetime.now
    modules = [
        iconeval._session,
        iconeval.main,
        iconeval.output_handling._summarize,
        iconeval.output_handling.publish_html,
    ]
    for module in modules:
        mock = mocker.patch.object(module, "datetime", autospec=True)
        mock.now.return_value = datetime(2000, 1, 1, 0, 0, 0)
        mock.fromtimestamp = datetime.fromtimestamp
        mock.strptime = datetime.strptime

    # datetime.fromtimestamp
    mock = mocker.patch.object(iconeval._simulation_info, "datetime", autospec=True)
    mock.fromtimestamp.return_value = datetime(2000, 1, 1, 0, 0, 0)

    # time
    modules = [iconeval.main, iconeval.output_handling.publish_html]
    for module in modules:
        mock = mocker.patch.object(module, "time", autospec=True)
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
def ignore_user_debug_log(monkeypatch: pytest.MonkeyPatch) -> None:
    def configure_logging(log_level: str, log_file: str | Path | None = None) -> None:
        _add_console_handler(log_level)

    monkeypatch.setattr(iconeval.main, "configure_logging", configure_logging)
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "configure_logging",
        configure_logging,
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
        "x-auth-token": "my-x-auth-token",
        "x-storage-url": "my-x-storage-url",
        "x-auth-token-expires": "42",
    }
    mock.RequestException = requests.RequestException
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


@pytest.fixture(autouse=True)
def remove_default_logger_handlers() -> None:
    """Remove all potential logging handlers before running any test."""
    logger.remove()


@pytest.fixture(autouse=True)
def temporary_swiftenv(
    monkeypatch: pytest.MonkeyPatch,
    lazy_shared_datadir: LazyDataDir,
) -> Path:
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "SWIFT_BASE_URL",
        "url/to/swift_storage/",
    )
    swiftenv_file = lazy_shared_datadir / "swiftenv"
    swiftenv_contents = dedent(
        """\
        #token expires on: Sat 01. Jan 00:00:01 UTC 2000
        setenv OS_AUTH_TOKEN this_is_a_very_nice_token
        setenv OS_STORAGE_URL url/to/swift_storage/my_folder
        setenv OS_AUTH_URL " "
        setenv OS_USERNAME " "
        setenv OS_PASSWORD " "
        """,
    )
    swiftenv_file.write_text(swiftenv_contents, encoding="utf-8")
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "SWIFT_ENV_FILE",
        swiftenv_file,
    )
    return swiftenv_file


# Manual fixtures


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
def recipe_template_dir() -> Path:
    return Path(str(files("iconeval"))).resolve() / "recipe_templates"


@pytest.fixture
def sample_data_path() -> Path:
    return Path(str(files("tests"))).resolve() / "sample_data"
