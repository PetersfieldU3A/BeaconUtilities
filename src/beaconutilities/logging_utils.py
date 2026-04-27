"""Logging configuration for BeaconUtilities."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

DEFAULT_LOG_FILE = Path("logs/beacon_utilities.log")
DEFAULT_LOG_LEVEL = "INFO"
_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 5


def configure_logging(
    log_file: Path = DEFAULT_LOG_FILE,
    log_level: str = DEFAULT_LOG_LEVEL,
) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_level.upper(), logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    handler_file = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
    )
    handler_file.setFormatter(formatter)

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler_file)
    root.addHandler(handler_console)
