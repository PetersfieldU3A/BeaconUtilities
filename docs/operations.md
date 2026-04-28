# Operations

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Safe Operations Policy

- **Always run `--dry-run` before the first live execution in any new environment.** This validates configuration, confirms extraction works, and shows what would be published without writing to WordPress.
- Do not edit `state/state.json` manually unless you understand the recovery impact.
- Keep Beacon credentials and WordPress application passwords secure and out of version control.
- One person should be responsible for approving any browser challenge during scheduled windows.

## Running a Sync

### Dry run (recommended first step)

```bash
.venv\Scripts\python.exe -m beaconutilities.cli sync --dry-run
```

Downloads from Beacon, parses, stages to SQLite (if enabled), and logs every record that *would* be published with no WordPress writes.

### Live run

```bash
.venv\Scripts\python.exe -m beaconutilities.cli sync
```

## Beacon -> SQLite Dry Run

Downloads both Beacon exports and stages every sheet into SQLite without any WordPress interaction. Useful for inspecting data, validating the download pipeline, or populating the database for ad-hoc analysis.

```bash
.venv\Scripts\python.exe -m beaconutilities.cli beacon-sqlite-dry-run
```

Override the database path for a one-off run:

```bash
.venv\Scripts\python.exe -m beaconutilities.cli beacon-sqlite-dry-run --db-path state/test.db
```

## Member Names Export

Downloads the Beacon Members export and writes `Member_Names.xlsx` to the configured output directory.

```bash
.venv\Scripts\python.exe -m beaconutilities.cli export-member-names
```

Override the output directory for a one-off run:

```bash
.venv\Scripts\python.exe -m beaconutilities.cli export-member-names --output-dir C:\Reports
```

Output directory resolution order:

1. `--output-dir` CLI flag (if provided)
2. `beacon_export.output_dir` in `config/config.ini`
3. Exit 1 with a clear error message if neither is set

The output file is always named `Member_Names.xlsx` with a worksheet called `Member Names` containing five columns: `mem_no`, `status`, `title`, `forename`, `surname`. Live output (2026-04-28): 1,815 rows.

## Full Beacon Backup Workbook

Downloads a single full-backup workbook from Beacon and saves it locally. The workbook is not loaded into SQLite.

```bash
.venv\Scripts\python.exe -m beaconutilities.cli backup-beacon
```

Output location resolution:

1. `--output-file` CLI flag (if provided)
2. `beacon_export.backup_output_dir` in `config/config.ini` with a timestamped Beacon-style file name such as `202604281322_Petersfield u3abackup.xlsx`
3. Fallback directory `outputs/` with the same timestamped Beacon-style file name

If `--output-file` points to a directory, BeaconUtilities still uses the timestamped Beacon-style file name inside that directory. If `--output-file` points to an `.xlsx` file, that exact file name is used.

Override for a one-off run:

```bash
.venv\Scripts\python.exe -m beaconutilities.cli backup-beacon --output-file C:\Backups
```

Force a specific file name only when needed:

```bash
.venv\Scripts\python.exe -m beaconutilities.cli backup-beacon --output-file C:\Backups\Beacon_Full_Backup.xlsx
```

## Scheduled Runs

### Windows (Task Scheduler)

Create a task that runs:

```text
<InstallPath>\.venv\Scripts\python.exe -m beaconutilities.cli sync
```

Use the option **Run only when user is logged on** to allow HID/browser approval if required.

### macOS (launchd)

Create a `.plist` in `~/Library/LaunchAgents/` pointing to the Python executable in `.venv/bin/python`.

## Monitoring

- Check `logs/beacon_utilities.log` after each run.
- Errors are logged at ERROR level; look for these first.
- A successful run ends with a log line containing `Sync complete`.
- The `state/state.json` file records the last sync result for quick status inspection, including the `staged` count.

## SQLite Staging Database

The optional SQLite staging database (`state/beacon_data.db`) stores every sheet from every downloaded workbook as its own table. Enable it in `config/config.ini`:

```ini
[database]
enabled = true
path = state/beacon_data.db
persist_across_sessions = false
```

| Option | Default | Effect |
| ------ | ------- | ------ |
| `enabled` | `false` | When `true`, all workbook sheets are loaded into SQLite |
| `path` | `state/beacon_data.db` | Location of the SQLite file |
| `persist_across_sessions` | `false` | `false` = tables dropped and recreated each run; `true` = rows accumulate |

### Tables

| Workbook | Sheet -> Table |
| -------- | ------------- |
| `members.xlsx` | `members`, `polls` |
| `groups.xlsx` | `groups`, `group_members`, `venues`, `faculties`, `group_ledgers` |

Each table has two prepended columns (`_id`, `_staged_at`) followed by one column per Excel header from row 1.

Query the database directly for ad-hoc analysis:

```bash
.venv\Scripts\python.exe -c "
import sqlite3
con = sqlite3.connect('state/beacon_data.db')
for row in con.execute('SELECT mem_no, status, forename, surname FROM members LIMIT 5'):
    print(row)
"
```

## Discovering Beacon Export Link Names

The `members_link_name` and `groups_link_name` values are used for Beacon's *Data export & backup* page. The full-backup flow can use a different Beacon option and is configured with `backup_section_link_name` and `backup_download_link_name`.

Live backup verification on 2026-04-28 saved:

- `outputs/202604281322_Petersfield u3abackup.xlsx`

| Key | Value |
| --- | ----- |
| `members_link_name` | `Members and addresses` |
| `groups_link_name` | `Groups, with members, venues` |
| `backup_section_link_name` | `Data export & backup` (or your backup menu option) |
| `backup_download_link_name` | `Backup all data` |

For a different U3A organisation, run the recorder and observe the link text clicked:

```bash
python -m invoke playwright-record --output scripts\members_download.py
```
