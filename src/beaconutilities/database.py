"""SQLite staging storage for Beacon exports.

This module allows extracted Beacon records to be persisted locally so they can
be reprocessed in multiple ways without re-downloading/parsing source files.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import BeaconRecord


def init_database(db_path: Path) -> None:
    """Create database schema if it does not already exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS staged_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                entity_type TEXT NOT NULL,
                record_id TEXT NOT NULL,
                fields_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_staged_records_entity_record
            ON staged_records(entity_type, record_id)
            """
        )


def store_records(db_path: Path, records: list[BeaconRecord]) -> int:
    """Persist records into SQLite and return inserted row count."""
    init_database(db_path)
    rows = [
        (
            record.entity_type.value,
            record.record_id,
            json.dumps(record.fields, ensure_ascii=False, default=str),
        )
        for record in records
    ]
    if not rows:
        return 0

    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO staged_records(entity_type, record_id, fields_json)
            VALUES (?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def clear_records(db_path: Path) -> None:
    """Remove all previously staged rows from SQLite."""
    init_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM staged_records")
