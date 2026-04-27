"""Tests for beaconutilities.mapping."""

from __future__ import annotations

import pytest

from beaconutilities.mapping import (
    MEMBER_ID_FIELD,
    GROUP_ID_FIELD,
    _slugify,
    map_group,
    map_member,
    map_record,
)
from beaconutilities.models import BeaconRecord, EntityType


class TestSlugify:
    def test_basic(self):
        assert _slugify("Hello World") == "hello-world"

    def test_strips_special_chars(self):
        assert _slugify("member-1001!") == "member-1001"

    def test_collapses_spaces(self):
        assert _slugify("a  b") == "a-b"

    def test_leading_trailing_hyphens_removed(self):
        assert _slugify("--hello--") == "hello"

    def test_numeric(self):
        assert _slugify("1001") == "1001"


class TestMapMember:
    def test_full_name_in_title(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert payload["title"] == "Alice Smith"

    def test_slug_contains_record_id(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert "1001" in payload["slug"]

    def test_slug_is_url_safe(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert " " not in payload["slug"]
        assert payload["slug"] == payload["slug"].lower()

    def test_status_is_publish(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert payload["status"] == "publish"

    def test_meta_contains_beacon_id(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert payload["meta"]["beacon_member_id"] == "1001"

    def test_meta_contains_email(self, sample_member_record):
        payload = map_member(sample_member_record)
        assert payload["meta"]["beacon_email"] == "alice@example.com"

    def test_missing_name_falls_back_to_record_id(self):
        r = BeaconRecord(record_id="999", entity_type=EntityType.MEMBER, fields={})
        payload = map_member(r)
        assert payload["title"] == "999"

    def test_partial_name(self):
        r = BeaconRecord(
            record_id="500",
            entity_type=EntityType.MEMBER,
            fields={"First Name": "Bob", "Last Name": None},
        )
        payload = map_member(r)
        assert payload["title"] == "Bob"


class TestMapGroup:
    def test_name_in_title(self, sample_group_record):
        payload = map_group(sample_group_record)
        assert payload["title"] == "Photography"

    def test_slug_contains_record_id(self, sample_group_record):
        payload = map_group(sample_group_record)
        assert "g42" in payload["slug"]

    def test_status_is_publish(self, sample_group_record):
        payload = map_group(sample_group_record)
        assert payload["status"] == "publish"

    def test_description_in_content(self, sample_group_record):
        payload = map_group(sample_group_record)
        assert "photography enthusiasts" in payload["content"].lower()

    def test_meta_contains_beacon_id(self, sample_group_record):
        payload = map_group(sample_group_record)
        assert payload["meta"]["beacon_group_id"] == "G42"

    def test_missing_name_falls_back_to_record_id(self):
        r = BeaconRecord(record_id="G99", entity_type=EntityType.GROUP, fields={})
        payload = map_group(r)
        assert payload["title"] == "G99"


class TestMapRecord:
    def test_dispatches_member(self, sample_member_record):
        payload = map_record(sample_member_record)
        assert "beacon_member_id" in payload["meta"]

    def test_dispatches_group(self, sample_group_record):
        payload = map_record(sample_group_record)
        assert "beacon_group_id" in payload["meta"]

    def test_unknown_entity_type_raises(self):
        r = BeaconRecord(record_id="x")
        r.entity_type = "invalid"  # bypass enum
        with pytest.raises(ValueError, match="No mapping defined"):
            map_record(r)
