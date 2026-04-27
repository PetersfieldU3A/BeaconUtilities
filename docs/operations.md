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

Downloads from Beacon, parses, stages to SQLite (if enabled), and logs every record that *would* be published — no WordPress writes.

### Live run

```bash
.venv\Scripts\python.exe -m beaconutilities.cli sync
```

## Scheduled Runs

### Windows (Task Scheduler)

Create a task that runs:

```
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

The optional SQLite staging database (`state/beacon_data.db`) holds all extracted records from the most recent sync. Enable it in `config/config.ini`:

```ini
[database]
enabled = true
path = state/beacon_data.db
persist_across_sessions = false
```

| Option | Default | Effect |
|--------|---------|--------|
| `enabled` | `false` | When `true`, all extracted records are written to SQLite before mapping |
| `path` | `state/beacon_data.db` | Location of the SQLite file |
| `persist_across_sessions` | `false` | `false` = table cleared each sync (session-style); `true` = rows accumulate |

Query the database directly for ad-hoc analysis:

```bash
.venv\Scripts\python.exe -c "
import sqlite3, json
con = sqlite3.connect('state/beacon_data.db')
for row in con.execute(\"SELECT entity_type, record_id, fields_json FROM staged_records LIMIT 5\"):
    print(row[0], row[1], json.loads(row[2]))
"
```

## Discovering Beacon Export Link Names

The `members_link_name` and `groups_link_name` values in `[beacon_export]` are the exact link text shown on Beacon's *Data export & backup* page. They have been confirmed for Petersfield U3A:

| Key | Value |
|-----|-------|
| `members_link_name` | `Members and addresses` |
| `groups_link_name` | `Groups, with members, venues` |

For a different U3A organisation, run the recorder and observe the link text clicked:

```bash
python -m invoke playwright-record --output scripts\members_download.py
```