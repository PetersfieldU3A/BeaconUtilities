"""Field mapping between Beacon records and WordPress target format.

Converts :class:`~beaconutilities.models.BeaconRecord` instances produced by
the Excel parser into WordPress REST API payload dicts ready for
:class:`~beaconutilities.wordpress.WordPressClient`.

.. note::
    Field name constants (e.g. :data:`MEMBER_ID_FIELD`) are placeholders that
    will be confirmed and updated once the Beacon Excel export artifacts are
    provided.  All mapping functions are pure (no I/O) so they are easy to
    unit-test against fixture data.
"""

from __future__ import annotations

import re

from .models import BeaconRecord, EntityType

# ---------------------------------------------------------------------------
# Field name constants — UPDATE once Excel artifacts are available
# ---------------------------------------------------------------------------

#: Excel column header that holds the unique member identifier.
MEMBER_ID_FIELD = "Member No"
#: Excel column header for member first name.
MEMBER_FIRST_NAME_FIELD = "First Name"
#: Excel column header for member last name.
MEMBER_LAST_NAME_FIELD = "Last Name"
#: Excel column header for member email address.
MEMBER_EMAIL_FIELD = "Email"
#: Excel column header that holds the unique group identifier.
GROUP_ID_FIELD = "Group Id"
#: Excel column header for the group name / title.
GROUP_NAME_FIELD = "Group Name"
#: Excel column header for the group description or summary.
GROUP_DESCRIPTION_FIELD = "Description"


# ---------------------------------------------------------------------------
# Public mapping functions
# ---------------------------------------------------------------------------

def map_member(record: BeaconRecord) -> dict:
    """Map a member :class:`~beaconutilities.models.BeaconRecord` to a WordPress payload.

    The ``slug`` field is derived from the member ID and used as an idempotency
    key by :class:`~beaconutilities.wordpress.WordPressClient`.

    Args:
        record: A record with ``entity_type == EntityType.MEMBER``.

    Returns:
        WordPress REST API payload dict.
    """
    first = str(record.get(MEMBER_FIRST_NAME_FIELD) or "").strip()
    last = str(record.get(MEMBER_LAST_NAME_FIELD) or "").strip()
    full_name = f"{first} {last}".strip() or record.record_id
    slug = _slugify(f"member-{record.record_id}")

    return {
        "title": full_name,
        "slug": slug,
        "status": "publish",
        "meta": {
            "beacon_member_id": record.record_id,
            "beacon_email": record.get(MEMBER_EMAIL_FIELD, ""),
            **record.fields,
        },
    }


def map_group(record: BeaconRecord) -> dict:
    """Map a group :class:`~beaconutilities.models.BeaconRecord` to a WordPress payload.

    Args:
        record: A record with ``entity_type == EntityType.GROUP``.

    Returns:
        WordPress REST API payload dict.
    """
    name = str(record.get(GROUP_NAME_FIELD) or record.record_id).strip()
    slug = _slugify(f"group-{record.record_id}")
    description = str(record.get(GROUP_DESCRIPTION_FIELD) or "").strip()

    return {
        "title": name,
        "slug": slug,
        "status": "publish",
        "content": description,
        "meta": {
            "beacon_group_id": record.record_id,
            **record.fields,
        },
    }


def map_record(record: BeaconRecord) -> dict:
    """Dispatch to the correct mapping function based on entity type.

    Args:
        record: Any :class:`~beaconutilities.models.BeaconRecord`.

    Returns:
        WordPress REST API payload dict.

    Raises:
        ValueError: If ``record.entity_type`` is not handled.
    """
    if record.entity_type == EntityType.MEMBER:
        return map_member(record)
    if record.entity_type == EntityType.GROUP:
        return map_group(record)
    raise ValueError(f"No mapping defined for entity type: {record.entity_type}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _slugify(value: str) -> str:
    """Convert *value* to a URL-safe lowercase slug."""
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")

