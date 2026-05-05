"""Shared pytest fixtures for BeaconUtilities tests."""

from __future__ import annotations

import json
from pathlib import Path

import openpyxl
import pytest

from beaconutilities.models import BeaconRecord, EntityType


# ---------------------------------------------------------------------------
# Configuration fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_config(tmp_path: Path) -> dict:
    """Minimal valid configuration dict for unit testing."""
    return {
        "beacon": {
            "portal_url": "https://u3abeacon.org.uk/password.php",
            "site_name": "TestU3A",
            "username": "testuser",
            "password": "testpass",
        },
        "beacon_export": {
            "members_link_name": "Members and addresses",
            "groups_link_name": "Groups, with members, venues",
            "backup_section_link_name": "Data export & backup",
            "backup_download_link_name": "Backup all data",
            "download_dir": str(tmp_path / "downloads"),
            "backup_output_dir": str(tmp_path / "outputs"),
        },
        "wordpress": {
            "site_url": "https://wp.example.com",
            "username": "wpuser",
            "application_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
            "members_post_type": "posts",
            "groups_post_type": "posts",
        },
    }


@pytest.fixture()
def incomplete_beacon_config() -> dict:
    """Config dict missing beacon password — triggers preflight failure."""
    return {
        "beacon": {
            "portal_url": "https://u3abeacon.org.uk/password.php",
            "site_name": "TestU3A",
            "username": "testuser",
            # password deliberately absent
        },
        "beacon_export": {
            "members_link_name": "Members and addresses",
            "groups_link_name": "Groups, with members, venues",
        },
    }


@pytest.fixture()
def incomplete_export_config() -> dict:
    """Config dict missing export link names — triggers preflight failure."""
    return {
        "beacon": {
            "portal_url": "https://u3abeacon.org.uk/password.php",
            "site_name": "TestU3A",
            "username": "testuser",
            "password": "testpass",
        },
        "beacon_export": {},
    }


@pytest.fixture()
def incomplete_wordpress_config(minimal_config: dict) -> dict:
    """Config dict missing WordPress application_password."""
    cfg = {k: dict(v) for k, v in minimal_config.items()}
    del cfg["wordpress"]["application_password"]
    return cfg


# ---------------------------------------------------------------------------
# Excel fixture factory
# ---------------------------------------------------------------------------

@pytest.fixture()
def make_excel(tmp_path: Path):
    """Factory that creates a simple .xlsx file with given sheet data.

    Usage::

        def test_foo(make_excel):
            path = make_excel({"Sheet1": [["Name", "Email"], ["Alice", "a@b.com"]]})
    """
    def _factory(sheets: dict[str, list[list]]) -> Path:
        wb = openpyxl.Workbook()
        for idx, (sheet_name, rows) in enumerate(sheets.items()):
            if idx == 0:
                ws = wb.active
                ws.title = sheet_name
            else:
                ws = wb.create_sheet(sheet_name)
            for row in rows:
                ws.append(row)
        path = tmp_path / "test_export.xlsx"
        wb.save(path)
        return path

    return _factory


# ---------------------------------------------------------------------------
# Record fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_member_record() -> BeaconRecord:
    return BeaconRecord(
        record_id="1001",
        entity_type=EntityType.MEMBER,
        fields={
            "Member No": "1001",
            "First Name": "Alice",
            "Last Name": "Smith",
            "Email": "alice@example.com",
        },
    )


@pytest.fixture()
def sample_group_record() -> BeaconRecord:
    return BeaconRecord(
        record_id="G42",
        entity_type=EntityType.GROUP,
        fields={
            "Group Id": "G42",
            "Group Name": "Photography",
            "Description": "A group for photography enthusiasts.",
        },
    )
