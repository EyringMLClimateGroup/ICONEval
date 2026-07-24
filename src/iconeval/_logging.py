"""Manage logging."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

logger = logger.opt(colors=True)


def configure_logging(log_level: str, log_file: str | Path | None = None) -> None:
    """Configure logging."""
    _add_console_handler(log_level)
    _add_file_handler(log_file)


def _add_console_handler(log_level: str) -> None:
    """Add console logging handler."""
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> |  <level>{message}</level>"
    )
    logger.add(sys.stdout, level=log_level.upper(), format=format_str, colorize=True)


def _add_file_handler(log_file: str | Path | None) -> None:
    """Add file logging handler."""
    if log_file is None:
        return
    log_file = Path(log_file).expanduser().resolve()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(log_file, level="DEBUG", rotation="500 MB", retention=10)
