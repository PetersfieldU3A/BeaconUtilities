"""Command line entrypoint for BeaconUtilities."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

from . import __version__ as APP_VERSION
from .config import load_config
from .logging_utils import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, configure_logging

__version__ = "0.0.1"
__author__ = "T. J. Willans"
__date__ = "2026-04-27"
__copyright__ = "Copyright 2026, MEADC Ltd"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BeaconUtilities — Beacon CRM automation")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/config.ini"),
        help="Path to configuration file (.ini preferred, .json supported)",
    )
    parser.add_argument(
        "--log-level",
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help="Path to log file",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {APP_VERSION}")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("sync", help="Run Beacon → WordPress sync")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(log_file=args.log_file, log_level=args.log_level)
    log = logging.getLogger(__name__)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    cfg = load_config(args.config)
    log.info("BeaconUtilities %s started", APP_VERSION)

    if args.command == "sync":
        log.info("Sync command not yet implemented.")


if __name__ == "__main__":
    main()
