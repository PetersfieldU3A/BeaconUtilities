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

### Missing export URLs

Log signs:

- `ValueError: members_export_url is not configured`

Action:

1. Run `python -m invoke playwright-record` to open the Beacon portal in a recorded browser session.
2. Navigate to the Members or Groups export page and copy the URL from the address bar.
3. Paste the URL into `config/config.ini` under `[beacon_export]`.

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
