from __future__ import annotations

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
