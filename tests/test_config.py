"""Tests for BeaconUtilities config loader."""

from __future__ import annotations

import tempfile
from pathlib import Path

from beaconutilities.config import load_config


def test_load_ini(tmp_path):
    cfg_file = tmp_path / "config.ini"
    cfg_file.write_text("[beacon]\nportal_url = https://example.com\nusername = test\n", encoding="utf-8")
    cfg = load_config(cfg_file)
    assert cfg["beacon"]["portal_url"] == "https://example.com"


def test_load_json(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text('{"beacon": {"portal_url": "https://example.com"}}', encoding="utf-8")
    cfg = load_config(cfg_file)
    assert cfg["beacon"]["portal_url"] == "https://example.com"
