"""Tests for beaconutilities.database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from beaconutilities.database import clear_records, init_database, store_records
from beaconutilities.models import BeaconRecord, EntityType


class TestInitDatabase:
    def test_creates_database_file_and_table(self, tmp_path: Path):
        db_path = tmp_path / "state" / "beacon_data.db"
        init_database(db_path)

        assert db_path.exists()
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='staged_records'"
            ).fetchone()
        assert row is not None


class TestStoreRecords:
    def test_inserts_records_and_returns_count(self, tmp_path: Path):
        db_path = tmp_path / "records.db"
        records = [
            BeaconRecord(
                record_id="1001",
                entity_type=EntityType.MEMBER,
                fields={"Member No": "1001", "First Name": "Alice"},
            ),
            BeaconRecord(
                record_id="G1",
                entity_type=EntityType.GROUP,
                fields={"Group Id": "G1", "Group Name": "Photography"},
            ),
        ]

        inserted = store_records(db_path, records)
        assert inserted == 2

        with sqlite3.connect(db_path) as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM staged_records").fetchone()[0]
        assert row_count == 2

    def test_returns_zero_for_empty_input(self, tmp_path: Path):
        db_path = tmp_path / "records.db"
        inserted = store_records(db_path, [])
        assert inserted == 0


class TestClearRecords:
    def test_deletes_existing_rows(self, tmp_path: Path):
        db_path = tmp_path / "records.db"
        records = [
            BeaconRecord(
                record_id="1001",
                entity_type=EntityType.MEMBER,
                fields={"Member No": "1001"},
            )
        ]
        store_records(db_path, records)
        clear_records(db_path)

        with sqlite3.connect(db_path) as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM staged_records").fetchone()[0]
        assert row_count == 0
