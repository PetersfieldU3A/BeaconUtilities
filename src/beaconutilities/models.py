"""Data models for BeaconUtilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EntityType(Enum):
    """Identifies the Beacon entity type represented by a record."""

    MEMBER = "member"
    GROUP = "group"


@dataclass
class BeaconRecord:
    """A single record extracted from a Beacon Excel export.

    Attributes:
        record_id: Unique identifier sourced from the Beacon data (e.g. member
                   number or group ID).  Used as the idempotency key when
                   creating or updating WordPress content.
        entity_type: The kind of Beacon entity this record represents.
        fields: Raw field values keyed by Excel column header name.  Field
                names are determined by the export file and will be confirmed
                once Excel artifacts are provided.
    """

    record_id: str = ""
    entity_type: EntityType = EntityType.MEMBER
    fields: dict = field(default_factory=dict)

    def get(self, key: str, default=None):
        """Convenience accessor for fields dict."""
        return self.fields.get(key, default)

