"""Command line entrypoint for BeaconUtilities."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__ as APP_VERSION
from .config import load_config
from .logging_utils import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, configure_logging
from .sync import (
    run_beacon_full_backup,
    run_beacon_to_sqlite_dry_run,
    run_export_member_names,
    run_sync,
)

__version__ = "0.0.5"
__author__ = "T. J. Willans"
__date__ = "2026-04-28"
__copyright__ = "Copyright 2026, MEADC Ltd"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BeaconUtilities — Beacon CRM to WordPress automation"
    )
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
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {APP_VERSION}"
    )

    subparsers = parser.add_subparsers(dest="command")
    sync_parser = subparsers.add_parser(
        "sync", help="Run Beacon → WordPress sync"
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Extract and map data without writing to WordPress. "
            "State is not updated. Recommended before first live run."
        ),
    )

    sqlite_parser = subparsers.add_parser(
        "beacon-sqlite-dry-run",
        help="Run Beacon export and stage all workbook sheets into SQLite",
    )
    sqlite_parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Optional SQLite DB path override (default uses config database.path)",
    )

    export_parser = subparsers.add_parser(
        "export-member-names",
        help="Export Member_Names.xlsx containing selected member columns",
    )
    export_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Output directory for Member_Names.xlsx. "
            "Overrides beacon_export.output_dir in config."
        ),
    )

    backup_parser = subparsers.add_parser(
        "backup-beacon",
        help="Download full Beacon backup workbook to configured output location",
    )
    backup_parser.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help=(
            "Output .xlsx file path, or a directory path. "
            "When a directory is provided, a Beacon-style timestamped filename is used. "
            "Overrides beacon_export.backup_output_dir in config."
        ),
    )
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
        dry_run: bool = getattr(args, "dry_run", False)
        result = run_sync(cfg, dry_run=dry_run)
        log.info("Sync result: %s", result)
        if result.get("status") not in ("ok", "partial"):
            sys.exit(1)
    elif args.command == "beacon-sqlite-dry-run":
        db_path: Path | None = getattr(args, "db_path", None)
        if db_path is not None:
            cfg.setdefault("database", {})["path"] = str(db_path)
        result = run_beacon_to_sqlite_dry_run(cfg)
        if result.get("status") in ("ok", "partial"):
            log.info(
                "Beacon -> SQLite dry run: %d table(s), %d row(s) staged",
                result.get("tables", 0),
                result.get("staged", 0),
            )
            for table, count in result.get("table_counts", {}).items():
                log.info("  %-30s %d rows", table, count)
        else:
            log.info("Beacon -> SQLite dry run result: %s", result)
        if result.get("status") not in ("ok", "partial"):
            sys.exit(1)
    elif args.command == "export-member-names":
        cli_output_dir: Path | None = getattr(args, "output_dir", None)
        cfg_output_dir = cfg.get("beacon_export", {}).get("output_dir")
        output_dir: Path | None = cli_output_dir or (
            Path(cfg_output_dir) if cfg_output_dir else None
        )

        if output_dir is None:
            log.error(
                "No output directory specified. Set beacon_export.output_dir in "
                "config.ini or pass --output-dir."
            )
            sys.exit(1)

        result = run_export_member_names(cfg, output_dir=output_dir)
        log.info("Member names export result: %s", result)
        if result.get("status") not in ("ok", "partial"):
            sys.exit(1)
    elif args.command == "backup-beacon":
        output_file: Path | None = getattr(args, "output_file", None)
        result = run_beacon_full_backup(cfg, output_file=output_file)
        log.info("Beacon full backup result: %s", result)
        if result.get("status") not in ("ok", "partial"):
            sys.exit(1)


if __name__ == "__main__":
    main()

