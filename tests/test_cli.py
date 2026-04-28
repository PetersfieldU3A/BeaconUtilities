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

    def test_beacon_sqlite_dry_run_command(self):
        parser = build_parser()
        args = parser.parse_args(["beacon-sqlite-dry-run"])
        assert args.command == "beacon-sqlite-dry-run"
        assert args.db_path is None

    def test_beacon_sqlite_dry_run_db_path_option(self):
        parser = build_parser()
        args = parser.parse_args([
            "beacon-sqlite-dry-run",
            "--db-path",
            "state/custom.db",
        ])
        assert args.command == "beacon-sqlite-dry-run"
        assert args.db_path == Path("state/custom.db")

    def test_export_member_names_requires_output_dir(self):
        parser = build_parser()
        args = parser.parse_args(["export-member-names"])
        assert args.command == "export-member-names"
        assert args.output_dir is None

    def test_export_member_names_output_dir_option(self):
        parser = build_parser()
        args = parser.parse_args([
            "export-member-names",
            "--output-dir",
            "exports",
        ])
        assert args.command == "export-member-names"
        assert args.output_dir == Path("exports")

    def test_backup_beacon_command(self):
        parser = build_parser()
        args = parser.parse_args(["backup-beacon"])
        assert args.command == "backup-beacon"
        assert args.output_file is None

    def test_backup_beacon_output_file_option(self):
        parser = build_parser()
        args = parser.parse_args([
            "backup-beacon",
            "--output-file",
            "outputs/custom_backup.xlsx",
        ])
        assert args.command == "backup-beacon"
        assert args.output_file == Path("outputs/custom_backup.xlsx")


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

    def test_beacon_sqlite_dry_run_calls_handler(self, minimal_config):
        with patch("sys.argv", ["beacon-utilities", "beacon-sqlite-dry-run"]):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_beacon_to_sqlite_dry_run",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        mock_run.assert_called_once_with(minimal_config)

    def test_beacon_sqlite_dry_run_db_path_override(self, minimal_config):
        with patch(
            "sys.argv",
            ["beacon-utilities", "beacon-sqlite-dry-run", "--db-path", "state/alt.db"],
        ):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_beacon_to_sqlite_dry_run",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        cfg = mock_run.call_args[0][0]
        assert Path(cfg["database"]["path"]) == Path("state/alt.db")

    def test_export_member_names_calls_handler(self, minimal_config):
        minimal_config["beacon_export"]["output_dir"] = "exports_from_config"
        with patch(
            "sys.argv",
            ["beacon-utilities", "export-member-names"],
        ):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_export_member_names",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        _, kwargs = mock_run.call_args
        assert kwargs["output_dir"] == Path("exports_from_config")

    def test_export_member_names_cli_output_dir_overrides_config(self, minimal_config):
        minimal_config["beacon_export"]["output_dir"] = "exports_from_config"
        with patch(
            "sys.argv",
            ["beacon-utilities", "export-member-names", "--output-dir", "exports_override"],
        ):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_export_member_names",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        _, kwargs = mock_run.call_args
        assert kwargs["output_dir"] == Path("exports_override")

    def test_export_member_names_exits_when_no_config_and_no_cli_output_dir(self, minimal_config):
        minimal_config["beacon_export"].pop("output_dir", None)
        with patch(
            "sys.argv",
            ["beacon-utilities", "export-member-names"],
        ):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch("beaconutilities.cli.configure_logging"):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
        assert exc_info.value.code == 1

    def test_backup_beacon_calls_handler(self, minimal_config):
        with patch("sys.argv", ["beacon-utilities", "backup-beacon"]):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_beacon_full_backup",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        _, kwargs = mock_run.call_args
        assert kwargs["output_file"] is None

    def test_backup_beacon_output_file_override(self, minimal_config):
        with patch(
            "sys.argv",
            [
                "beacon-utilities",
                "backup-beacon",
                "--output-file",
                "outputs/custom_backup.xlsx",
            ],
        ):
            with patch("beaconutilities.cli.load_config", return_value=minimal_config):
                with patch(
                    "beaconutilities.cli.run_beacon_full_backup",
                    return_value={"status": "ok"},
                ) as mock_run:
                    with patch("beaconutilities.cli.configure_logging"):
                        main()
        _, kwargs = mock_run.call_args
        assert kwargs["output_file"] == Path("outputs/custom_backup.xlsx")

