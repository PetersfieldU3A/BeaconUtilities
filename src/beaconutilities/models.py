"""Data models for BeaconUtilities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BeaconRecord:
    """Represents a single record retrieved from Beacon."""
    record_id: str = ""
    fields: dict = field(default_factory=dict)
