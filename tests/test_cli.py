"""Tests for beaconutilities.cli."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from beaconutilities.cli import build_parser, main


class TestBuildParser:
    def test_default_config_path(self):
        parser = build_parser()
        args = parser.parse_args(["sync"])
        assert args.config == Path("config/config.ini")

    def test_custom_config_path(self):
        parser = build_parser()
        args = parser.parse_args(["--config", "my/config.ini", "sync"])
        assert args.config == Path("my/config.ini")

    def test_sync_dry_run_flag(self):
        parser = build_parser()
        args = parser.parse_args(["sync", "--dry-run"])
        assert args.dry_run is True

    def test_sync_dry_run_defaults_false(self):
        parser = build_parser()
        args = parser.parse_args(["sync"])
        assert args.dry_run is False

    def test_no_command_dest_is_none(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_log_level_choices(self):
        parser = build_parser()
        args = parser.parse_args(["--log-level", "DEBUG", "sync"])
        assert args.log_level == "DEBUG"

    def test_invalid_log_level_exits(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--log-level", "VERBOSE", "sync"])


class TestMain:
    def test_no_command_prints_help_and_exits_zero(self, capsys):
        with patch("sys.argv", ["beacon-utilities"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0

    def test_sync_command_calls_run_sync(self, minimal_config, tmp_path):
        cfg_file = tmp_path / "config.ini"
        cfg_file.write_text(
            "[beacon]\nportal_url=https://b.example.com\nusername=u\npassword=p\n"
            "[beacon_export]\nmembers_export_url=https://x\ngroups_export_url=https://y\n"
            "[wordpress]\nsite_url=https://wp.example.com\nusername=u\napplication_password=p\n",
            encoding="utf-8",
        )
        with patch("sys.argv", ["beacon-utilities", "--config", str(cfg_file), "sync"]):
            with patch("beaconutilities.cli.run_sync", return_value={"status": "ok"}) as mock_sync:
                with patch("beaconutilities.cli.configure_logging"):
                    main()
        mock_sync.assert_called_once()
        _, kwargs = mock_sync.call_args
        assert kwargs.get("dry_run") is False or mock_sync.call_args[0][1] is False

    def test_sync_dry_run_passed_to_run_sync(self, tmp_path):
        cfg_file = tmp_path / "config.ini"
        cfg_file.write_text(
            "[beacon]\nportal_url=https://b.example.com\nusername=u\npassword=p\n"
            "[beacon_export]\nmembers_export_url=https://x\ngroups_export_url=https://y\n"
            "[wordpress]\nsite_url=https://wp.example.com\nusername=u\napplication_password=p\n",
            encoding="utf-8",
        )
        with patch(
            "sys.argv",
            ["beacon-utilities", "--config", str(cfg_file), "sync", "--dry-run"],
        ):
            with patch(
                "beaconutilities.cli.run_sync", return_value={"status": "ok"}
            ) as mock_sync:
                with patch("beaconutilities.cli.configure_logging"):
                    main()
        call_args = mock_sync.call_args
        dry_run_value = call_args[1].get("dry_run", call_args[0][1] if len(call_args[0]) > 1 else None)
        assert dry_run_value is True

    def test_failed_status_exits_nonzero(self, tmp_path):
        cfg_file = tmp_path / "config.ini"
        cfg_file.write_text(
            "[beacon]\nportal_url=https://b.example.com\nusername=u\npassword=p\n"
            "[beacon_export]\nmembers_export_url=https://x\ngroups_export_url=https://y\n"
            "[wordpress]\nsite_url=https://wp.example.com\nusername=u\napplication_password=p\n",
            encoding="utf-8",
        )
        with patch(
            "sys.argv", ["beacon-utilities", "--config", str(cfg_file), "sync"]
        ):
            with patch(
                "beaconutilities.cli.run_sync",
                return_value={"status": "preflight_failed"},
            ):
                with patch("beaconutilities.cli.configure_logging"):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
        assert exc_info.value.code == 1

