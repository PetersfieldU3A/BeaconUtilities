"""Tests for beaconutilities.beacon_scraper (non-browser paths)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from beaconutilities.beacon_scraper import (
    _download_export,
    _download_export_from_section,
    _is_login_page,
    download_beacon_backup,
    download_beacon_exports,
)


# ---------------------------------------------------------------------------
# _is_login_page
# ---------------------------------------------------------------------------

class TestIsLoginPage:
    def test_detects_password_php(self):
        assert _is_login_page("https://u3abeacon.org.uk/password.php") is True

    def test_detects_login_in_url(self):
        assert _is_login_page("https://example.com/login") is True

    def test_detects_signin(self):
        assert _is_login_page("https://example.com/signin") is True

    def test_detects_sign_in_hyphen(self):
        assert _is_login_page("https://example.com/sign-in") is True

    def test_returns_false_for_dashboard(self):
        assert _is_login_page("https://u3abeacon.org.uk/memberlist.php") is False

    def test_returns_false_for_export_page(self):
        assert _is_login_page("https://u3abeacon.org.uk/dataexport.php") is False

    def test_case_insensitive(self):
        assert _is_login_page("https://example.com/LOGIN") is True


# ---------------------------------------------------------------------------
# download_beacon_exports — validation before browser is opened
# ---------------------------------------------------------------------------

class TestDownloadBeaconExportsValidation:
    """Tests for RuntimeErrors raised before any browser interaction."""

    def _base_config(self, tmp_path):
        return {
            "beacon": {
                "portal_url": "https://u3abeacon.org.uk/password.php",
                "site_name": "TestU3A",
                "username": "user",
                "password": "pass",
            },
            "beacon_export": {
                "members_link_name": "Members and addresses",
                "groups_link_name": "Groups",
            },
        }

    def test_raises_when_site_name_empty(self, tmp_path):
        cfg = self._base_config(tmp_path)
        cfg["beacon"]["site_name"] = ""
        with pytest.raises(RuntimeError, match="site_name"):
            download_beacon_exports(cfg, tmp_path)

    def test_raises_when_site_name_missing(self, tmp_path):
        cfg = self._base_config(tmp_path)
        del cfg["beacon"]["site_name"]
        with pytest.raises(RuntimeError, match="site_name"):
            download_beacon_exports(cfg, tmp_path)

    def test_raises_when_members_link_name_empty(self, tmp_path):
        cfg = self._base_config(tmp_path)
        cfg["beacon_export"]["members_link_name"] = ""
        with pytest.raises(RuntimeError, match="members_link_name"):
            download_beacon_exports(cfg, tmp_path)

    def test_raises_when_members_link_name_missing(self, tmp_path):
        cfg = self._base_config(tmp_path)
        del cfg["beacon_export"]["members_link_name"]
        with pytest.raises(RuntimeError, match="members_link_name"):
            download_beacon_exports(cfg, tmp_path)

    def test_raises_when_groups_link_name_empty(self, tmp_path):
        cfg = self._base_config(tmp_path)
        cfg["beacon_export"]["groups_link_name"] = ""
        with pytest.raises(RuntimeError, match="groups_link_name"):
            download_beacon_exports(cfg, tmp_path)

    def test_raises_when_groups_link_name_missing(self, tmp_path):
        cfg = self._base_config(tmp_path)
        del cfg["beacon_export"]["groups_link_name"]
        with pytest.raises(RuntimeError, match="groups_link_name"):
            download_beacon_exports(cfg, tmp_path)


class TestDownloadBeaconBackupValidation:
    def _base_config(self):
        return {
            "beacon": {
                "portal_url": "https://u3abeacon.org.uk/password.php",
                "site_name": "TestU3A",
                "username": "user",
                "password": "pass",
            },
            "beacon_export": {
                "backup_section_link_name": "Data export & backup",
                "backup_download_link_name": "Backup all data",
                "backup_link_name": "Backup all data",
            },
        }

    def test_raises_when_site_name_missing(self, tmp_path):
        cfg = self._base_config()
        del cfg["beacon"]["site_name"]
        with pytest.raises(RuntimeError, match="site_name"):
            download_beacon_backup(cfg, tmp_path / "backup.xlsx")

    def test_raises_when_backup_link_name_missing(self, tmp_path):
        cfg = self._base_config()
        del cfg["beacon_export"]["backup_download_link_name"]
        del cfg["beacon_export"]["backup_link_name"]
        with pytest.raises(RuntimeError, match="backup_download_link_name"):
            download_beacon_backup(cfg, tmp_path / "backup.xlsx")

    def test_uses_legacy_backup_link_name_fallback(self, tmp_path):
        cfg = self._base_config()
        del cfg["beacon_export"]["backup_download_link_name"]
        del cfg["beacon"]["site_name"]
        with pytest.raises(RuntimeError, match="site_name"):
            download_beacon_backup(cfg, tmp_path / "backup.xlsx")


class TestDownloadExportHelper:
    def _mock_page_with_download(self, tmp_path: Path, failure_msg: str | None = None):
        page = MagicMock()
        page.get_by_role.return_value = MagicMock()

        download = MagicMock()
        download.failure.return_value = failure_msg

        def _save_as(path):
            Path(path).write_bytes(b"xlsx")

        download.save_as.side_effect = _save_as

        download_info = MagicMock()
        download_info.value = download

        cm = MagicMock()
        cm.__enter__.return_value = download_info
        cm.__exit__.return_value = False
        page.expect_download.return_value = cm
        return page

    def test_download_export_saves_file_and_returns_destination(self, tmp_path):
        page = self._mock_page_with_download(tmp_path, failure_msg=None)
        dest = tmp_path / "members.xlsx"

        out = _download_export(page, "Members and addresses", dest)

        assert out == dest
        assert dest.exists()
        page.expect_download.assert_called_once()
        page.wait_for_load_state.assert_called()

    def test_download_export_raises_on_download_failure(self, tmp_path):
        page = self._mock_page_with_download(tmp_path, failure_msg="network")
        dest = tmp_path / "members.xlsx"

        with pytest.raises(RuntimeError, match="Download failed"):
            _download_export(page, "Members and addresses", dest)

    def test_download_export_from_section_uses_section_link_name(self, tmp_path):
        page = self._mock_page_with_download(tmp_path, failure_msg=None)
        dest = tmp_path / "backup.xlsx"

        out = _download_export_from_section(
            page,
            "Backups",
            "Backup all data",
            dest,
        )

        assert out == dest
        first_call = page.get_by_role.call_args_list[0]
        assert first_call.kwargs == {"name": "Backups"}
