"""Tests for beaconutilities.sync — orchestration layer.

All external I/O (Playwright, WordPress HTTP) is mocked so tests run
offline and without side effects.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import openpyxl
import pytest

from beaconutilities.sync import run_sync


def _write_excel(path: Path, rows: list[list]) -> None:
    """Helper: write a single-sheet .xlsx at *path*."""
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


class TestRunSyncPreflight:
    def test_returns_preflight_failed_on_bad_beacon_config(self, tmp_path):
        cfg = {"beacon": {}, "beacon_export": {}, "wordpress": {}}
        result = run_sync(cfg)
        assert result["status"] == "preflight_failed"

    def test_returns_preflight_failed_on_bad_wordpress_config(self, minimal_config):
        minimal_config["wordpress"]["site_url"] = ""
        with patch("beaconutilities.sync.download_beacon_exports") as mock_dl:
            # preflight_wordpress should fail before download is called
            result = run_sync(minimal_config, dry_run=False)
        assert result["status"] == "preflight_failed"
        mock_dl.assert_not_called()


class TestRunSyncDownloadFailure:
    def test_returns_download_failed_on_exception(self, minimal_config):
        with patch(
            "beaconutilities.sync.download_beacon_exports",
            side_effect=RuntimeError("Connection refused"),
        ):
            result = run_sync(minimal_config)
        assert result["status"] == "download_failed"
        assert "Connection refused" in result["errors"][0]


class TestRunSyncDryRun:
    def test_dry_run_skips_wordpress(self, minimal_config, tmp_path):
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [
            ["Member No", "First Name", "Last Name", "Email"],
            ["1001", "Alice", "Smith", "alice@example.com"],
        ])
        _write_excel(groups_xlsx, [
            ["Group Id", "Group Name", "Description"],
            ["G1", "Photography", "Camera fans"],
        ])

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config") as mock_wp:
                result = run_sync(minimal_config, dry_run=True)

        mock_wp.assert_not_called()
        assert result["dry_run"] is True
        assert result["members_extracted"] == 1
        assert result["groups_extracted"] == 1
        assert result["staged"] == 0
        assert result["published"] == 0

    def test_dry_run_does_not_update_state(self, minimal_config, tmp_path):
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.save_state") as mock_save:
                run_sync(minimal_config, dry_run=True)

        mock_save.assert_not_called()


class TestRunSyncLivePublish:
    def test_publishes_all_records(self, minimal_config, tmp_path):
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [
            ["Member No", "First Name", "Last Name", "Email"],
            ["1001", "Alice", "Smith", "alice@example.com"],
            ["1002", "Bob", "Jones", "bob@example.com"],
        ])
        _write_excel(groups_xlsx, [
            ["Group Id", "Group Name", "Description"],
            ["G1", "Photography", ""],
        ])

        mock_wp_client = MagicMock()
        mock_wp_client.upsert_post.return_value = {"id": 1}

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config", return_value=mock_wp_client):
                with patch("beaconutilities.sync.save_state"):
                    result = run_sync(minimal_config, dry_run=False)

        assert result["status"] == "ok"
        assert result["published"] == 3  # 2 members + 1 group
        assert mock_wp_client.upsert_post.call_count == 3
        assert result["staged"] == 0

    def test_partial_status_on_publish_error(self, minimal_config, tmp_path):
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        mock_wp_client = MagicMock()
        mock_wp_client.upsert_post.side_effect = Exception("HTTP 500")

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config", return_value=mock_wp_client):
                with patch("beaconutilities.sync.save_state"):
                    result = run_sync(minimal_config, dry_run=False)

        assert result["status"] == "partial"
        assert len(result["errors"]) > 0


class TestRunSyncDatabaseStaging:
    def test_stages_records_when_enabled(self, minimal_config, tmp_path):
        minimal_config["database"] = {
            "enabled": "true",
            "path": str(tmp_path / "state" / "beacon_data.db"),
        }
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        mock_wp_client = MagicMock()
        mock_wp_client.upsert_post.return_value = {"id": 1}

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config", return_value=mock_wp_client):
                with patch("beaconutilities.sync.save_state"):
                    result = run_sync(minimal_config, dry_run=False)

        assert result["staged"] == 2

    def test_non_persistent_mode_replaces_rows_each_run(self, minimal_config, tmp_path):
        db_path = tmp_path / "state" / "beacon_data.db"
        minimal_config["database"] = {
            "enabled": "true",
            "path": str(db_path),
            "persist_across_sessions": "false",
        }
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            first = run_sync(minimal_config, dry_run=True)
        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            second = run_sync(minimal_config, dry_run=True)

        assert first["staged"] == 2
        assert second["staged"] == 2

        import sqlite3

        with sqlite3.connect(db_path) as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM staged_records").fetchone()[0]
        assert row_count == 2

    def test_persistent_mode_accumulates_rows(self, minimal_config, tmp_path):
        db_path = tmp_path / "state" / "beacon_data.db"
        minimal_config["database"] = {
            "enabled": "true",
            "path": str(db_path),
            "persist_across_sessions": "true",
        }
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            run_sync(minimal_config, dry_run=True)
        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            run_sync(minimal_config, dry_run=True)

        import sqlite3

        with sqlite3.connect(db_path) as conn:
            row_count = conn.execute("SELECT COUNT(*) FROM staged_records").fetchone()[0]
        assert row_count == 4

    def test_sets_partial_if_staging_fails(self, minimal_config, tmp_path):
        minimal_config["database"] = {
            "enabled": "true",
            "path": str(tmp_path / "state" / "beacon_data.db"),
        }
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        mock_wp_client = MagicMock()
        mock_wp_client.upsert_post.return_value = {"id": 1}

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config", return_value=mock_wp_client):
                with patch("beaconutilities.sync.store_records", side_effect=RuntimeError("db down")):
                    with patch("beaconutilities.sync.save_state"):
                        result = run_sync(minimal_config, dry_run=False)

        assert result["status"] == "partial"
        assert any("db_staging" in msg for msg in result["errors"])

    def test_state_saved_after_live_sync(self, minimal_config, tmp_path):
        members_xlsx = tmp_path / "members.xlsx"
        groups_xlsx = tmp_path / "groups.xlsx"
        _write_excel(members_xlsx, [["Member No"], ["1001"]])
        _write_excel(groups_xlsx, [["Group Id"], ["G1"]])

        mock_wp_client = MagicMock()
        mock_wp_client.upsert_post.return_value = {"id": 1}

        with patch(
            "beaconutilities.sync.download_beacon_exports",
            return_value={"members": members_xlsx, "groups": groups_xlsx},
        ):
            with patch("beaconutilities.sync.client_from_config", return_value=mock_wp_client):
                with patch("beaconutilities.sync.save_state") as mock_save:
                    with patch("beaconutilities.sync.load_state", return_value={}):
                        run_sync(minimal_config, dry_run=False)

        mock_save.assert_called_once()
        saved_state = mock_save.call_args[0][1]
        assert "last_sync" in saved_state
