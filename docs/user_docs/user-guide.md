# User Guide

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This guide assumes installation is already complete and successful.
If you still need setup steps, use the Installation Guide first.

## Purpose

BeaconUtilities retrieves data from Beacon (the U3A CRM) and uses it to update pages on the Petersfield U3A WordPress website automatically.  Phase I covers Members and Groups.

## How to run beacon-utilities

### Dry run (recommended before first live run)

A dry run performs the full extraction and mapping cycle but makes **no changes** to WordPress.  Use this to verify configuration and inspect the log output before committing.

```bash
cd <InstallPath>
.\.venv\Scripts\python.exe -m beaconutilities.cli sync --dry-run
```

The log will show every record that *would* be published, including its mapped slug and title.  No WordPress API calls are made.

### Live run

```bash
cd <InstallPath>
.\.venv\Scripts\python.exe -m beaconutilities.cli sync
```

Publishes all extracted Members and Groups to WordPress using slug-based idempotency (safe to re-run).

### Beacon → SQLite dry run

Downloads both Beacon exports and stages every workbook sheet into the local SQLite database — no WordPress interaction required. Useful for validating the download pipeline or inspecting raw Beacon data.

```bash
.\.venv\Scripts\python.exe -m beaconutilities.cli beacon-sqlite-dry-run
```

Use `--db-path` to save to an alternative database file:

```bash
.\.venv\Scripts\python.exe -m beaconutilities.cli beacon-sqlite-dry-run --db-path state\test.db
```

### Export Member Names

Downloads the Beacon Members export and writes `Member_Names.xlsx` to the output directory configured in `config/config.ini` (`beacon_export.output_dir`). The file contains five columns: `mem_no`, `status`, `title`, `forename`, `surname`.

```bash
.\.venv\Scripts\python.exe -m beaconutilities.cli export-member-names
```

Override the output directory for a one-off run:

```bash
.\.venv\Scripts\python.exe -m beaconutilities.cli export-member-names --output-dir C:\Reports
```

## Where the log file is

```text
<InstallPath>/logs/beacon_utilities.log
```

Rotating logs are kept; up to 5 backup files at ~1 MB each.

## How to read a log line

```text
YYYY-MM-DD HH:MM:SS | LEVEL | logger_name | message
```

### Meaning of levels

- INFO: expected progress messages
- WARNING: run continued, but something needs attention
- ERROR: run stopped or a safety gate was triggered

## Common issues and what to do

### Beacon login failure

Log signs:

- ERROR during Playwright login step

Action:

1. Verify Beacon credentials in `config/config.ini`.
2. Check that the Beacon portal URL is correct.
3. Re-run with `--log-level DEBUG` to see browser interaction detail.

### Missing export link names

Log signs:

- `ValueError: members_link_name is not configured`

Action:

1. Run `python -m invoke playwright-record` to open the Beacon portal in a recorded browser session.
2. Navigate to the *Data export & backup* page and note the exact link text for Members and Groups exports.
3. Set `members_link_name` and `groups_link_name` in `config/config.ini` under `[beacon_export]`.

### WordPress API failure

Log signs:

- HTTP 401, 403, or 5xx errors during WordPress POST/PUT

Action:

1. Verify WordPress application password in `config/config.ini`.
2. Confirm the WordPress REST API is enabled on the site.
3. Retry after a short wait for transient 5xx errors.

## Safe operations rules

- Always use `--dry-run` on a new installation before the first live run.
- Do not edit `state/state.json` manually unless you understand the recovery impact.
- Keep Beacon credentials and WordPress application passwords secure and out of version control.
