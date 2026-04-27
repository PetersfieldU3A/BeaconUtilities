"""Runtime state management for BeaconUtilities."""

from __future__ import annotations

import json
from pathlib import Path


def load_state(state_path: Path) -> dict:
    """Load state from a JSON file, returning an empty dict if absent."""
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state_path: Path, state: dict) -> None:
    """Persist state to a JSON file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
