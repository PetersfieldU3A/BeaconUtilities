"""Sync orchestration for BeaconUtilities.

Coordinates the full Phase I Beacon → WordPress workflow:

1. Preflight validation
2. Beacon login + Excel export download (via Playwright)
3. Excel parsing → :class:`~beaconutilities.models.BeaconRecord` lists
4. Field mapping → WordPress REST API payloads
5. WordPress upsert (skipped in dry-run mode)
6. State persistence
"""

from __future__ import annotations

import logging
from pathlib import Path

from .beacon_scraper import download_beacon_exports
from .database import clear_records, store_records
from .excel_parser import parse_sheet
from .mapping import map_record
from .models import BeaconRecord, EntityType
from .preflight import preflight_beacon, preflight_wordpress
from .state import load_state, save_state
from .wordpress import client_from_config

log = logging.getLogger(__name__)

#: Default path for the runtime state file.
DEFAULT_STATE_PATH = Path("state/state.json")


def run_sync(config: dict, dry_run: bool = False) -> dict:
    """Orchestrate a full Beacon → WordPress sync cycle.

    Args:
        config: Loaded configuration dictionary produced by
                :func:`~beaconutilities.config.load_config`.
        dry_run: When ``True`` data is extracted and mapped but nothing is
                 written to WordPress.  State is not updated in dry-run mode.

    Returns:
        Result summary dict with keys:
        ``status``, ``dry_run``, ``members_extracted``, ``groups_extracted``,
        ``published``, ``errors``.
    """
    log.info("Sync started (dry_run=%s)", dry_run)

    result: dict = {
        "status": "ok",
        "dry_run": dry_run,
        "members_extracted": 0,
        "groups_extracted": 0,
        "staged": 0,
        "published": 0,
        "errors": [],
    }

    # ── 1. Preflight ─────────────────────────────────────────────────────────
    if not preflight_beacon(config):
        result["status"] = "preflight_failed"
        return result
    if not dry_run and not preflight_wordpress(config):
        result["status"] = "preflight_failed"
        return result

    # ── 2. Download Excel exports ─────────────────────────────────────────────
    download_dir = Path(
        config.get("beacon_export", {}).get("download_dir", "downloads")
    )
    try:
        export_paths = download_beacon_exports(config, download_dir)
    except Exception as exc:
        log.error("Beacon export failed: %s", exc)
        result["status"] = "download_failed"
        result["errors"].append(str(exc))
        return result

    # ── 3. Parse ──────────────────────────────────────────────────────────────
    member_records = _parse_export(export_paths["members"], EntityType.MEMBER, result)
    group_records = _parse_export(export_paths["groups"], EntityType.GROUP, result)

    result["members_extracted"] = len(member_records)
    result["groups_extracted"] = len(group_records)
    log.info(
        "Extracted %d member(s) and %d group(s)",
        result["members_extracted"],
        result["groups_extracted"],
    )

    # ── 4. Optional staging to SQLite ───────────────────────────────────────
    db_cfg = config.get("database", {})
    db_enabled = _is_truthy(db_cfg.get("enabled", "false"))
    if db_enabled:
        db_path = Path(db_cfg.get("path", "state/beacon_data.db"))
        persist_across_sessions = _is_truthy(
            db_cfg.get("persist_across_sessions", "false")
        )
        try:
            if not persist_across_sessions:
                clear_records(db_path)
            staged = store_records(db_path, member_records + group_records)
            result["staged"] = staged
            log.info(
                "Staged %d record(s) into %s (persist_across_sessions=%s)",
                staged,
                db_path,
                persist_across_sessions,
            )
        except Exception as exc:
            log.error("Database staging failed: %s", exc)
            result["errors"].append(f"db_staging: {exc}")
            result["status"] = "partial"

    if dry_run:
        log.info("Dry-run: skipping WordPress publish and state update")
        return result

    # ── 5 & 6. Map + Publish ──────────────────────────────────────────────────
    wp_client = client_from_config(config)
    wp_cfg = config.get("wordpress", {})
    members_post_type = wp_cfg.get("members_post_type", "posts")
    groups_post_type = wp_cfg.get("groups_post_type", "posts")

    all_records = [
        (record, members_post_type) for record in member_records
    ] + [
        (record, groups_post_type) for record in group_records
    ]

    for record, post_type in all_records:
        try:
            payload = map_record(record)
            wp_client.upsert_post(payload, post_type=post_type)
            result["published"] += 1
        except Exception as exc:
            msg = f"{record.entity_type.value} id={record.record_id}: {exc}"
            log.error("Publish failed — %s", msg)
            result["errors"].append(msg)
            result["status"] = "partial"

    # ── 7. State ──────────────────────────────────────────────────────────────
    state = load_state(DEFAULT_STATE_PATH)
    state["last_sync"] = {
        "status": result["status"],
        "members_extracted": result["members_extracted"],
        "groups_extracted": result["groups_extracted"],
        "published": result["published"],
        "errors": result["errors"],
    }
    save_state(DEFAULT_STATE_PATH, state)

    log.info("Sync complete: %s", result)
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_export(
    file_path: Path,
    entity_type: EntityType,
    result: dict,
) -> list[BeaconRecord]:
    """Parse all sheets of an Excel export file into BeaconRecord instances.

    Each sheet in the file contributes rows; the first column of each row is
    used as the ``record_id``.  Parsing errors are recorded in *result* but
    do not abort the sync.
    """
    from .excel_parser import list_sheets

    records: list[BeaconRecord] = []
    try:
        sheets = list_sheets(file_path)
    except Exception as exc:
        log.error("Cannot read %s: %s", file_path, exc)
        result["errors"].append(str(exc))
        return records

    for sheet in sheets:
        try:
            rows = parse_sheet(file_path, sheet)
        except Exception as exc:
            log.warning("Skipping sheet '%s' in %s: %s", sheet, file_path, exc)
            result["errors"].append(f"Sheet '{sheet}': {exc}")
            continue

        for row in rows:
            # Use the first non-empty column value as the record ID
            record_id = str(next((v for v in row.values() if v is not None), ""))
            records.append(
                BeaconRecord(
                    record_id=record_id,
                    entity_type=entity_type,
                    fields=row,
                )
            )

    return records


def _is_truthy(value: object) -> bool:
    """Parse common INI-style truthy values."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

