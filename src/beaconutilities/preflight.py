"""Preflight checks for BeaconUtilities.

Validates configuration before any Beacon or WordPress interaction is attempted.
All checks return ``True`` on success and log a clear error message on failure.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

_REQUIRED_BEACON_KEYS = ["portal_url", "site_name", "username", "password"]
_REQUIRED_EXPORT_KEYS = ["members_link_name", "groups_link_name"]
_REQUIRED_WORDPRESS_KEYS = ["site_url", "username", "application_password"]


def preflight_beacon(config: dict) -> bool:
    """Validate that required Beacon configuration keys are present and non-empty.

    Args:
        config: Loaded configuration dict.

    Returns:
        ``True`` if all checks pass, ``False`` otherwise.
    """
    ok = True
    beacon_cfg = config.get("beacon", {})
    missing = [k for k in _REQUIRED_BEACON_KEYS if not beacon_cfg.get(k)]
    if missing:
        log.error("Beacon config missing required keys: %s", missing)
        ok = False

    export_cfg = config.get("beacon_export", {})
    missing_export = [k for k in _REQUIRED_EXPORT_KEYS if not export_cfg.get(k)]
    if missing_export:
        log.error(
            "beacon_export config missing required keys: %s. "
            "Run 'invoke playwright-record' to discover the link text values.",
            missing_export,
        )
        ok = False

    if ok:
        log.info("Beacon preflight OK")
    return ok


def preflight_wordpress(config: dict) -> bool:
    """Validate that required WordPress configuration keys are present and non-empty.

    Args:
        config: Loaded configuration dict.

    Returns:
        ``True`` if all checks pass, ``False`` otherwise.
    """
    wp_cfg = config.get("wordpress", {})
    missing = [k for k in _REQUIRED_WORDPRESS_KEYS if not wp_cfg.get(k)]
    if missing:
        log.error("WordPress config missing required keys: %s", missing)
        return False
    log.info("WordPress preflight OK")
    return True

