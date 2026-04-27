# Architecture

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Phase I: Beacon → WordPress

The Phase I architecture implements a unidirectional pipeline with an optional local SQLite staging layer:

```
Beacon Portal
    │  Playwright (login + Excel download)
    ▼
excel_parser  →  BeaconRecord (models)
    │
    ├──▶ database (SQLite staging — optional, configurable)
    │
    │  mapping
    ▼
WordPressClient (wordpress)
    │  REST API
    ▼
WordPress Site
```

State and logging are cross-cutting concerns present throughout the pipeline.

## Package Structure

```
src/beaconutilities/
    __init__.py       Package metadata and version
    cli.py            CLI entrypoint: sync, beacon-sqlite-dry-run, export-member-names
    config.py         INI/JSON configuration loader
    logging_utils.py  Rotating file + console logging
    models.py         BeaconRecord dataclass; EntityType enum (MEMBER, GROUP)
    excel_parser.py   Reads Beacon Excel exports into list[dict] per sheet
    beacon_scraper.py Playwright login + automated Excel download
    database.py       Workbook-driven SQLite staging; each Excel sheet loaded as its own table
    mapping.py        BeaconRecord → WordPress REST API payload
    wordpress.py      WordPress REST API client (upsert by slug)
    preflight.py      Pre-run configuration validation
    state.py          JSON-backed runtime state (resumable, auditable)
    sync.py           Orchestrates the full extract → transform → publish cycle
```

## Data Flow

1. **CLI** parses arguments and calls `run_sync(config, dry_run)`.
2. **Preflight** validates that all required config keys are present for both Beacon and WordPress.
3. **beacon_scraper** uses Playwright to log in to the Beacon portal and download two Excel files (Members, Groups). Confirmed login flow: accept cookie consent → Select2 site picker (`site_name`) → `#ecUsername` / `#ecPassword` → *Enter* button → *Data export & backup* → click named export link.
4. **excel_parser** reads each sheet of each file and returns rows as plain dicts keyed by column header.
5. **sync** constructs `BeaconRecord` instances from the parsed rows, assigning `EntityType.MEMBER` or `EntityType.GROUP`.
6. **database** (optional) loads every sheet of every downloaded workbook into a local SQLite file. Each sheet becomes its own table (e.g. `members`, `polls`, `groups`, `group_members`, `venues`, `faculties`, `group_ledgers`). Set `persist_across_sessions = false` (default) to drop and recreate tables on each run; `true` to accumulate rows across runs.
7. **mapping** converts each `BeaconRecord` to a WordPress REST API payload dict including a slug derived from the Beacon record ID (idempotency key).
8. **wordpress** calls `GET /wp-json/wp/v2/{post_type}?slug=...` to check existence, then `POST` or `PUT` accordingly.
9. **state** persists the sync result summary to `state/state.json`.

## Configuration

Runtime configuration is stored in `config/config.ini` (gitignored). A template is provided at `config/config.example.ini`.

| Section | Purpose |
|---|---|
| `[beacon]` | Portal URL, `site_name` (Select2 dropdown label), username, password |
| `[beacon_export]` | `members_link_name`, `groups_link_name` (exact export link text), `download_dir`, `output_dir` (default output directory for exports such as Member_Names.xlsx) |
| `[database]` | `enabled`, `path`, `persist_across_sessions` — controls optional SQLite staging |
| `[wordpress]` | Site URL, username, application password, post types for members and groups |

### Confirmed export link names (Petersfield U3A)

| Export | Link text |
|--------|-----------|
| Members | `Members and addresses` |
| Groups | `Groups, with members, venues` |

## SQLite Staging Database

When `[database] enabled = true`, every sheet of every downloaded workbook is loaded into a local SQLite file. This allows the same download to be reprocessed for multiple output scenarios without re-downloading from Beacon.

### Table layout

Each worksheet becomes its own table. The table name is the sanitised sheet name (lower-case, alphanumeric only). Two standard columns are prepended:

| Column | Type | Notes |
|--------|------|-------|
| `_id` | INTEGER | Auto-increment primary key |
| `_staged_at` | TEXT | `CURRENT_TIMESTAMP` of insert |
| *(Excel headers)* | TEXT | One column per header in row 1 of the sheet |

### Tables created from live Beacon workbooks

| Workbook | Sheet → Table |
|----------|---------------|
| `members.xlsx` | `members`, `polls` |
| `groups.xlsx` | `groups`, `group_members`, `venues`, `faculties`, `group_ledgers` |

### Session vs. persistent mode

| `persist_across_sessions` | Behaviour |
|--------------------------|-----------|
| `false` (default) | Tables are dropped and recreated on each run — only the current run's data is present |
| `true` | Rows accumulate across runs — useful for historical trending |

Live confirmed record counts (2026-04-28): 1,815 member rows across 7 tables from 2 workbooks.

## CLI Commands

Three subcommands are available:

| Command | Description |
|---------|-------------|
| `sync [--dry-run]` | Full Beacon → WordPress pipeline (optional SQLite staging, optional dry-run) |
| `beacon-sqlite-dry-run [--db-path PATH]` | Download Beacon exports and stage all workbook sheets into SQLite. No WordPress writes. |
| `export-member-names [--output-dir PATH]` | Download Beacon exports and write `Member_Names.xlsx` to the configured output directory. |

### Member Names Export

`export-member-names` produces a single workbook:

| Property | Value |
|----------|-------|
| Output file | `Member_Names.xlsx` (in `beacon_export.output_dir` or `--output-dir`) |
| Worksheet name | `Member Names` |
| Columns | `mem_no`, `status`, `title`, `forename`, `surname` |

Live output (2026-04-28): 1,815 rows written.

## State

Run state is persisted as JSON in `state/state.json` (gitignored). Structure:

```json
{
  "last_sync": {
    "status": "ok",
    "members_extracted": 3242,
    "groups_extracted": 1382,
    "staged": 4624,
    "published": 0,
    "errors": []
  }
}
```

Do not edit this file manually unless you understand the recovery impact.

## Logging

Rotating log files are written to `logs/beacon_utilities.log` (gitignored). Up to 5 backups are retained at ~1 MB each.