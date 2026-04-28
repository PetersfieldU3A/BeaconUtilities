# User Guide

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This guide assumes installation is already complete and successful.
If you still need setup steps, use the Installation Guide first.

## Purpose

BeaconUtilities retrieves data from Beacon (the U3A CRM) and uses it to update pages on the Petersfield U3A WordPress website automatically.  Phase I covers Members and Groups.

## How to run beacon-utilities

The installer creates launcher scripts for normal operations:

- Windows: `run.ps1`
- macOS / Linux: `run.sh`

### Dry run (recommended before first live run)

A dry run performs the full extraction and mapping cycle but makes **no changes** to WordPress. Use this to verify configuration and inspect the log output before committing.

Windows:

```powershell
cd <InstallPath>
.\run.ps1 sync --dry-run
```

macOS / Linux:

```bash
cd <InstallPath>
./run.sh sync --dry-run
```

The log will show every record that *would* be published, including its mapped slug and title. No WordPress API calls are made.

### Live run

Windows:

```powershell
cd <InstallPath>
.\run.ps1 sync
```

macOS / Linux:

```bash
cd <InstallPath>
./run.sh sync
```

Publishes all extracted Members and Groups to WordPress using slug-based idempotency (safe to re-run).

### Beacon -> SQLite dry run

Downloads both Beacon exports and stages every workbook sheet into the local SQLite database with no WordPress interaction. Useful for validating the download pipeline or inspecting raw Beacon data.

Windows:

```powershell
.\run.ps1 beacon-sqlite-dry-run
```

macOS / Linux:

```bash
./run.sh beacon-sqlite-dry-run
```

Use `--db-path` to save to an alternative database file:

Windows:

```powershell
.\run.ps1 beacon-sqlite-dry-run --db-path state\test.db
```

macOS / Linux:

```bash
./run.sh beacon-sqlite-dry-run --db-path state/test.db
```

### Export Member Names

Downloads the Beacon Members export and writes `Member_Names.xlsx` to the output directory configured in `config/config.ini` (`beacon_export.output_dir`). The file contains five columns: `mem_no`, `status`, `title`, `forename`, `surname`.

Windows:

```powershell
.\run.ps1 export-member-names
```

macOS / Linux:

```bash
./run.sh export-member-names
```

Override the output directory for a one-off run:

Windows:

```powershell
.\run.ps1 export-member-names --output-dir C:\Reports
```

macOS / Linux:

```bash
./run.sh export-member-names --output-dir /tmp/reports
```

### Full Beacon Backup Workbook

Downloads the Beacon full backup workbook and saves it to the directory configured in `config/config.ini` (`beacon_export.backup_output_dir`).
If your Beacon tenant uses a different menu option for backups, set `beacon_export.backup_section_link_name` and `beacon_export.backup_download_link_name` to the exact visible link text.
When BeaconUtilities chooses the name itself, it uses a Beacon-style timestamped file name such as `202604281322_Petersfield u3abackup.xlsx`.

Windows:

```powershell
.\run.ps1 backup-beacon
```

macOS / Linux:

```bash
./run.sh backup-beacon
```

Override the output path for a one-off run:

Pass a directory to keep the timestamped Beacon-style file name:

Windows:

```powershell
.\run.ps1 backup-beacon --output-file C:\Backups
```

macOS / Linux:

```bash
./run.sh backup-beacon --output-file /tmp/backups
```

Pass an explicit `.xlsx` file path only when you want to force a specific file name:

Windows:

```powershell
.\run.ps1 backup-beacon --output-file C:\Backups\Beacon_Full_Backup.xlsx
```

macOS / Linux:

```bash
./run.sh backup-beacon --output-file /tmp/backups/beacon_backup.xlsx
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

### Beacon backup link not found

Log signs:

- `ValueError` mentioning `backup_section_link_name` or `backup_download_link_name`

Action:

1. Run `python -m invoke playwright-record`.
2. Navigate through the Beacon backup flow manually.
3. Copy the exact visible text for the backup menu option into `backup_section_link_name`.
4. Copy the exact visible text for the final download link into `backup_download_link_name`.

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
