"""Playwright-based Beacon portal automation for data extraction.

Downloads Excel export files for Members and Groups by automating the Beacon
CRM portal login and export navigation flow.

Login flow (discovered via ``invoke playwright-record``):

1. Navigate to the Beacon password page (``portal_url``).
2. Accept optional cookies if the consent banner is present.
3. Select the U3A site from the Select2 dropdown (``site_name``).
4. Fill ``#ecUsername`` and ``#ecPassword``, then click the *Enter* button.
5. Navigate to *Data export & backup*.
6. Click the named export link (``members_link_name`` / ``groups_link_name``)
   and capture the resulting file download.

To discover the ``groups_link_name`` value, run::

    python -m invoke playwright-record --output scripts\\groups_download.py

and observe the link text clicked to trigger the groups Excel download.
"""

from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import Download, sync_playwright

log = logging.getLogger(__name__)

#: Link text for the Beacon data export section (stable across all orgs).
_EXPORT_SECTION_LINK = "Data export & backup"

#: Cookie consent button name (shown on first visit).
_COOKIE_BUTTON_NAME = "I Accept optional cookies"


def download_beacon_exports(
    config: dict,
    download_dir: Path,
) -> dict[str, Path]:
    """Log in to Beacon and download Excel exports for Members and Groups.

    Args:
        config: Loaded configuration dictionary.  Must contain a ``[beacon]``
                section with ``portal_url``, ``site_name``, ``username``, and
                ``password`` keys, and a ``[beacon_export]`` section with
                ``members_link_name`` and ``groups_link_name``.
        download_dir: Directory where downloaded .xlsx files will be saved.
                      Created automatically if it does not exist.

    Returns:
        Dict with keys ``'members'`` and ``'groups'`` pointing to the
        downloaded file paths.

    Raises:
        RuntimeError: If Beacon login fails or a required config value is absent.
        KeyError: If required config sections are absent.
    """
    beacon_cfg = config["beacon"]
    export_cfg = config.get("beacon_export", {})

    portal_url = beacon_cfg["portal_url"].rstrip("/")
    site_name = beacon_cfg.get("site_name", "").strip()
    username = beacon_cfg["username"]
    password = beacon_cfg["password"]

    members_link = export_cfg.get("members_link_name", "").strip()
    groups_link = export_cfg.get("groups_link_name", "").strip()

    if not site_name:
        raise RuntimeError(
            "beacon.site_name is not configured in config/config.ini."
        )
    if not members_link:
        raise RuntimeError(
            "beacon_export.members_link_name is not configured. "
            "Run 'invoke playwright-record' to discover the link text."
        )
    if not groups_link:
        raise RuntimeError(
            "beacon_export.groups_link_name is not configured. "
            "Run 'invoke playwright-record --output scripts/groups_download.py' "
            "to discover the link text for the groups export."
        )

    headless = str(beacon_cfg.get("headless", "true")).strip().lower() not in ("false", "0", "no", "off")

    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    downloaded: dict[str, Path] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # ── Login ────────────────────────────────────────────────────────
            log.info("Navigating to Beacon portal: %s", portal_url)
            page.goto(portal_url, wait_until="networkidle")

            _accept_cookies_if_present(page)

            log.info("Selecting site: %s", site_name)
            page.locator("#select2-cbSite-container").click()
            page.get_by_role("searchbox", name="Search").fill(site_name)
            page.get_by_role("option", name=site_name).click()

            log.info("Logging in as %s", username)
            page.locator("#ecUsername").fill(username)
            page.locator("#ecPassword").fill(password)
            page.get_by_role("button", name="Enter").click()
            page.wait_for_load_state("networkidle")

            if _is_login_page(page.url):
                raise RuntimeError(
                    "Beacon login failed — verify credentials and site_name "
                    "in config/config.ini"
                )
            log.info("Login successful; current URL: %s", page.url)

            # ── Members export ───────────────────────────────────────────────
            log.info("Downloading members export (link: '%s')", members_link)
            downloaded["members"] = _download_export(
                page, members_link, download_dir / "members.xlsx"
            )

            # ── Groups export ────────────────────────────────────────────────
            log.info("Downloading groups export (link: '%s')", groups_link)
            downloaded["groups"] = _download_export(
                page, groups_link, download_dir / "groups.xlsx"
            )

            # ── Logout ───────────────────────────────────────────────────────
            try:
                page.get_by_role("link", name="Log Out").click()
                log.info("Logged out successfully")
            except Exception:
                log.warning("Logout step failed — session will expire naturally")

        finally:
            context.close()
            browser.close()

    return downloaded


def download_beacon_backup(
    config: dict,
    output_file: Path,
    backup_download_link_name: str | None = None,
) -> Path:
    """Log in to Beacon and download a single full-backup workbook.

    Args:
        config: Loaded configuration dictionary.
        output_file: Destination ``.xlsx`` path for the downloaded backup.
        backup_download_link_name: Optional Beacon download link text override.
            If not provided, ``beacon_export.backup_download_link_name`` is used.

    Returns:
        Path to the saved backup workbook.

    Raises:
        RuntimeError: If required values are missing, login fails, or download fails.
    """
    beacon_cfg = config["beacon"]
    export_cfg = config.get("beacon_export", {})

    portal_url = beacon_cfg["portal_url"].rstrip("/")
    site_name = beacon_cfg.get("site_name", "").strip()
    username = beacon_cfg["username"]
    password = beacon_cfg["password"]
    backup_section_link = export_cfg.get("backup_section_link_name", _EXPORT_SECTION_LINK).strip()
    backup_link = (
        backup_download_link_name
        or export_cfg.get("backup_download_link_name", "")
    ).strip()

    if not site_name:
        raise RuntimeError(
            "beacon.site_name is not configured in config/config.ini."
        )
    if not backup_link:
        raise RuntimeError(
            "beacon_export.backup_download_link_name is not configured. "
            "Run 'invoke playwright-record' to discover the full-backup link text."
        )
    if not backup_section_link:
        raise RuntimeError(
            "beacon_export.backup_section_link_name is empty. "
            "Set it to the Beacon navigation link text for the backup page."
        )

    headless = str(beacon_cfg.get("headless", "true")).strip().lower() not in ("false", "0", "no", "off")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            log.info("Navigating to Beacon portal: %s", portal_url)
            page.goto(portal_url, wait_until="networkidle")

            _accept_cookies_if_present(page)

            log.info("Selecting site: %s", site_name)
            page.locator("#select2-cbSite-container").click()
            page.get_by_role("searchbox", name="Search").fill(site_name)
            page.get_by_role("option", name=site_name).click()

            log.info("Logging in as %s", username)
            page.locator("#ecUsername").fill(username)
            page.locator("#ecPassword").fill(password)
            page.get_by_role("button", name="Enter").click()
            page.wait_for_load_state("networkidle")

            if _is_login_page(page.url):
                raise RuntimeError(
                    "Beacon login failed — verify credentials and site_name "
                    "in config/config.ini"
                )

            log.info("Downloading full Beacon backup (link: '%s')", backup_link)
            saved_file = _download_export_from_section(
                page,
                backup_section_link,
                backup_link,
                output_file,
            )

            try:
                page.get_by_role("link", name="Log Out").click()
                log.info("Logged out successfully")
            except Exception:
                log.warning("Logout step failed — session will expire naturally")

            return saved_file

        finally:
            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _accept_cookies_if_present(page) -> None:
    """Click the optional-cookie consent button if visible; silently skip otherwise."""
    try:
        btn = page.get_by_role("button", name=_COOKIE_BUTTON_NAME)
        if btn.is_visible(timeout=3_000):
            btn.click()
            log.debug("Cookie consent accepted")
    except Exception:
        pass  # banner not present or already dismissed


def _download_export(page, link_name: str, dest: Path) -> Path:
    """Navigate to the export section, download, then return Home.

    Navigates to *Data export & backup*, triggers the named download link,
    then clicks *Home* to return to the dashboard — leaving the page in a
    clean state for the next call or logout.

    Args:
        page: Active Playwright page (must be logged in and at the dashboard).
        link_name: Exact link text as it appears in Beacon's *Data export & backup* page.
        dest: Local file path to save the download to.

    Returns:
        The saved file path (*dest*).

    Raises:
        RuntimeError: If the download fails.
    """
    return _download_export_from_section(page, _EXPORT_SECTION_LINK, link_name, dest)


def _download_export_from_section(
    page,
    section_link_name: str,
    link_name: str,
    dest: Path,
) -> Path:
    """Navigate to a section, download from a named link, then return Home."""
    page.get_by_role("link", name=section_link_name).click()
    page.wait_for_load_state("networkidle")

    with page.expect_download(timeout=60_000) as download_info:
        page.get_by_role("link", name=link_name).click()

    download: Download = download_info.value
    if download.failure():
        raise RuntimeError(
            f"Download failed for link '{link_name}': {download.failure()}"
        )
    download.save_as(dest)
    log.info("Saved '%s' export to %s (%d bytes)", link_name, dest, dest.stat().st_size)

    page.get_by_role("link", name="Home").click()
    page.wait_for_load_state("networkidle")

    return dest


def _is_login_page(url: str) -> bool:
    """Return True if *url* looks like the Beacon login/password page."""
    lower = url.lower()
    return any(token in lower for token in ("password.php", "login", "signin", "sign-in"))

