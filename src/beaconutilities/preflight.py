"""Preflight checks for BeaconUtilities."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def preflight_beacon(config: dict) -> bool:
    """Validate that required Beacon configuration keys are present."""
    required = ["portal_url", "username"]
    beacon_cfg = config.get("beacon", {})
    missing = [k for k in required if not beacon_cfg.get(k)]
    if missing:
        log.error("Beacon config missing required keys: %s", missing)
        return False
    log.info("Beacon preflight OK")
    return True
