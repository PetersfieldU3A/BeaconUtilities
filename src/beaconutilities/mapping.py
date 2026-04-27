"""Field mapping between Beacon records and WordPress target format."""

from __future__ import annotations

from .models import BeaconRecord


def map_to_wordpress(record: BeaconRecord) -> dict:
    """Map a Beacon record to a WordPress REST API payload.

    Extend this function as the WordPress integration schema is defined.
    """
    return {
        "title": record.fields.get("name", ""),
        "status": "publish",
        "meta": record.fields,
    }
