"""Tests for beaconutilities.preflight."""

from __future__ import annotations

import pytest

from beaconutilities.preflight import (
    preflight_beacon,
    preflight_beacon_backup,
    preflight_wordpress,
)


class TestPreflightBeacon:
    def test_passes_with_valid_config(self, minimal_config):
        assert preflight_beacon(minimal_config) is True

    def test_fails_when_portal_url_missing(self, minimal_config):
        del minimal_config["beacon"]["portal_url"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_username_missing(self, minimal_config):
        del minimal_config["beacon"]["username"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_site_name_missing(self, minimal_config):
        del minimal_config["beacon"]["site_name"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_password_missing(self, minimal_config):
        del minimal_config["beacon"]["password"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_beacon_section_absent(self):
        assert preflight_beacon({}) is False

    def test_fails_when_members_export_url_missing(self, minimal_config):
        del minimal_config["beacon_export"]["members_link_name"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_groups_export_url_missing(self, minimal_config):
        del minimal_config["beacon_export"]["groups_link_name"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_when_export_section_absent(self, minimal_config):
        del minimal_config["beacon_export"]
        assert preflight_beacon(minimal_config) is False

    def test_fails_on_empty_string_values(self, minimal_config):
        minimal_config["beacon"]["portal_url"] = ""
        assert preflight_beacon(minimal_config) is False

    def test_logs_missing_keys(self, minimal_config, caplog):
        del minimal_config["beacon"]["password"]
        import logging
        with caplog.at_level(logging.ERROR, logger="beaconutilities.preflight"):
            preflight_beacon(minimal_config)
        assert "password" in caplog.text


class TestPreflightWordPress:
    def test_passes_with_valid_config(self, minimal_config):
        assert preflight_wordpress(minimal_config) is True

    def test_fails_when_site_url_missing(self, minimal_config):
        del minimal_config["wordpress"]["site_url"]
        assert preflight_wordpress(minimal_config) is False

    def test_fails_when_username_missing(self, minimal_config):
        del minimal_config["wordpress"]["username"]
        assert preflight_wordpress(minimal_config) is False

    def test_fails_when_application_password_missing(self, incomplete_wordpress_config):
        assert preflight_wordpress(incomplete_wordpress_config) is False

    def test_fails_when_wordpress_section_absent(self):
        assert preflight_wordpress({}) is False


class TestPreflightBeaconBackup:
    def test_passes_with_valid_config(self, minimal_config):
        assert preflight_beacon_backup(minimal_config) is True

    def test_fails_when_beacon_credentials_missing(self, minimal_config):
        del minimal_config["beacon"]["password"]
        assert preflight_beacon_backup(minimal_config) is False

    def test_fails_when_backup_link_name_missing(self, minimal_config):
        del minimal_config["beacon_export"]["backup_download_link_name"]
        del minimal_config["beacon_export"]["backup_link_name"]
        assert preflight_beacon_backup(minimal_config) is False

    def test_passes_with_legacy_backup_link_name_fallback(self, minimal_config):
        del minimal_config["beacon_export"]["backup_download_link_name"]
        assert preflight_beacon_backup(minimal_config) is True
