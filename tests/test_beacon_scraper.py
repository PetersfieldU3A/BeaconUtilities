"""Tests for beaconutilities.beacon_scraper (non-browser paths)."""

from __future__ import annotations

import pytest

from beaconutilities.beacon_scraper import _is_login_page, download_beacon_exports


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
