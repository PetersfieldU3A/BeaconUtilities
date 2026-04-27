# Project Overview

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Purpose

To programmatically access Beacon, the U3A CRM, and use that data to automatically populate pages on the Petersfield U3A WordPress website. As Beacon does not provide a user-accessible API, Playwright browser automation is used to mimic user interaction and trigger data exports.

## Phase I Scope

Phase I delivers a proof-of-concept for the **Beacon → WordPress** workflow:

- **In scope:** Members and Groups data only.
- **Out of scope:** WordPress → Beacon workflows are explicitly deferred to later phases.
- **Extraction method:** Playwright fully automates Beacon login and triggers Excel export downloads for both Members and Groups via named link clicks on the *Data export & backup* page. No manual steps are required.
- **PoC acceptance:** Dry-run passes, then a controlled publish to a staging WordPress site creates Member and Group content with correct metadata.

## Core Objectives

1. **Beacon Automation** — Use Playwright to log in to Beacon and download Members and Groups data as Excel exports.
2. **Data Transformation** — Parse Excel exports and map Beacon fields to WordPress REST API payloads.
3. **WordPress Integration** — Create or update WordPress content via the REST API using an idempotency key derived from Beacon record IDs.
4. **Reliability** — Robust error handling, dry-run mode, and rotating log files so failures are visible and recoverable.
5. **Cross-Platform Compatibility** — Operate on Windows 11 and macOS.

## System Architecture

### Components

- **Beacon Portal + Playwright** (`beacon_scraper`) — Automates login and Excel export download via confirmed named link selectors.
- **Excel Parser** (`excel_parser`) — Reads downloaded .xlsx files into structured row dicts.
- **Data Models** (`models`) — `BeaconRecord` with `EntityType` (MEMBER / GROUP).
- **SQLite Staging** (`database`) — Optional local database for intermediate record storage. Supports session and persistent modes.
- **Field Mapper** (`mapping`) — Maps `BeaconRecord` instances to WordPress REST API payloads.
- **WordPress Client** (`wordpress`) — Issues create/update requests with idempotent slug-based lookup.
- **Sync Orchestrator** (`sync`) — Coordinates the full extract → stage → transform → publish cycle.
- **State Manager** (`state`) — JSON-backed state for resumable, auditable runs.
- **CLI** (`cli`) — `beacon-utilities sync [--dry-run]` entrypoint.

### Workflow

1. Preflight: validate Beacon and WordPress configuration.
2. Login to Beacon via Playwright and download Members and Groups Excel exports.
3. Parse each export sheet into `BeaconRecord` instances.
4. **Optional:** Stage records to the local SQLite database for multi-scenario reprocessing without re-downloading.
5. Map each record to a WordPress REST API payload.
6. Dry-run: log payloads, skip WordPress writes.
7. Live run: upsert each payload to WordPress; record ID is the idempotency slug.
8. Persist run state to `state/state.json` and log result summary.

### Live Validation (2026-04-27)

Full dry-run against the Petersfield U3A Beacon portal confirmed:

- Members downloaded: `downloads/members.xlsx` (333,407 bytes)
- Groups downloaded: `downloads/groups.xlsx` (91,090 bytes)
- Records staged: 3,242 members · 1,382 groups · **4,624 total**