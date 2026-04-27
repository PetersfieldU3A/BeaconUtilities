"""Tests for beaconutilities.models."""

from __future__ import annotations

from beaconutilities.models import BeaconRecord, EntityType


class TestEntityType:
    def test_member_value(self):
        assert EntityType.MEMBER.value == "member"

    def test_group_value(self):
        assert EntityType.GROUP.value == "group"


class TestBeaconRecord:
    def test_defaults(self):
        r = BeaconRecord()
        assert r.record_id == ""
        assert r.entity_type == EntityType.MEMBER
        assert r.fields == {}

    def test_explicit_construction(self):
        r = BeaconRecord(
            record_id="42",
            entity_type=EntityType.GROUP,
            fields={"Group Name": "Painting"},
        )
        assert r.record_id == "42"
        assert r.entity_type == EntityType.GROUP
        assert r.fields["Group Name"] == "Painting"

    def test_get_existing_field(self):
        r = BeaconRecord(fields={"Email": "x@y.com"})
        assert r.get("Email") == "x@y.com"

    def test_get_missing_field_returns_default(self):
        r = BeaconRecord()
        assert r.get("NonExistent") is None
        assert r.get("NonExistent", "fallback") == "fallback"

    def test_fields_are_independent_between_instances(self):
        r1 = BeaconRecord(fields={"A": 1})
        r2 = BeaconRecord(fields={"B": 2})
        assert "A" not in r2.fields
        assert "B" not in r1.fields

    def test_mutable_fields_default_not_shared(self):
        """Default factory must produce a new dict each time."""
        r1 = BeaconRecord()
        r2 = BeaconRecord()
        r1.fields["x"] = 1
        assert "x" not in r2.fields
