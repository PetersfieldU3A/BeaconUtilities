"""Configuration loading for BeaconUtilities."""

from __future__ import annotations

import configparser
import json
from pathlib import Path


def load_config(config_path: Path) -> dict:
    """Load configuration from an INI or JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()
    if suffix == ".json":
        return json.loads(config_path.read_text(encoding="utf-8"))

    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")
    return {section: dict(parser[section]) for section in parser.sections()}
