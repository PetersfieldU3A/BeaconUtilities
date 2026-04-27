# Appendix 1: Development Notes

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix is a rolling log of decisions, assumptions, and rationale recorded as the project evolves.  A new entry is added whenever a significant decision is made or changed.  Minor implementation choices do not require an entry.

---

## 2026-04-27 — Phase I Scope Locked

**Decision:** Phase I is restricted to a Beacon → WordPress proof of concept covering Members and Groups only.

**Rationale:** The fastest path to demonstrating value is a working unidirectional sync.  WordPress → Beacon workflows introduce bidirectional complexity that is not required for the initial proof of concept.

**Impact:** All Phase I implementation, testing, and documentation targets the Beacon → WordPress direction only.

**Follow-up:** WordPress → Beacon direction is recorded in the Phase II backlog (requirements discovery only at this stage).

---

## 2026-04-27 — Extraction Method: Excel Download

**Decision:** Beacon data is extracted via automated Excel export download rather than HTML scraping.

**Rationale:** Beacon provides export functionality for Members and Groups as Excel files.  Downloading structured exports is more reliable and maintainable than scraping HTML tables.

**Impact:** New module `excel_parser.py` handles .xlsx parsing.  `beacon_scraper.py` uses Playwright to automate login and trigger the download.  `openpyxl` added as a runtime dependency.

**Follow-up:** Export URLs and exact selectors will be locked in after running `invoke playwright-record` against the live Beacon portal.  Example Excel artifacts to be stored in `tests/fixtures/` when provided.

---

## 2026-04-27 — Test Coverage Gate

**Decision:** CI requires **>80% overall unit test coverage**.  `invoke ci` fails if the threshold is not met.

**Rationale:** Provides confidence in core business logic (mapping, preflight, state) while keeping the gate achievable for a PoC iteration pace.

**Impact:** `pyproject.toml` and `tasks.py` updated.  All new modules must ship with corresponding test files.

**Follow-up:** Review threshold at Phase I completion; raise to 85% for v1.0.

---

## 2026-04-27 — Documentation as Definition of Done

**Decision:** Documentation is a first-class deliverable.  A change is not complete until relevant docs (overview, architecture, development, user docs, appendices) are updated.

**Rationale:** Prevents documentation drift and ensures the project remains maintainable by others.

**Impact:** Definition of Done checklist added to `docs/development.md`.

**Follow-up:** Review documentation completeness at each milestone before version bump.

---

## 2026-04-27 — MkDocs Serve Port

**Decision:** Local documentation server runs on port **8020** (changed from default 8000).

**Rationale:** Avoids conflict with other local services commonly running on port 8000.

**Impact:** `tasks.py` `docs` task updated with `--dev-addr 127.0.0.1:8020`.

**Follow-up:** None.

---

## 2026-04-27 — WordPress Idempotency Strategy

**Decision:** WordPress posts are identified by a URL slug derived from the Beacon record ID (e.g. `member-1001`, `group-g42`).  The client does a GET by slug before deciding to POST or PUT.

**Rationale:** Simple to implement, deterministic, and survives re-runs without creating duplicate posts.

**Impact:** All mapping functions must produce a `slug` key.  `wordpress.py` `upsert_post` enforces this.

**Follow-up:** If custom post types are used in WordPress, confirm they are accessible via the REST API at their expected endpoints.

---

## 2026-04-27 — Beacon Login Flow Confirmed via Playwright Recording

**Decision:** The confirmed Beacon login sequence is: navigate to `https://u3abeacon.org.uk/password.php` → accept cookie consent banner → Select2 site picker (`#select2-cbSite-container`) → type `site_name` → fill `#ecUsername` / `#ecPassword` → click the *Enter* button.  Export downloads are triggered by clicking the *Data export & backup* navigation link, then clicking the named export link.

**Rationale:** Placeholder selectors from initial implementation were replaced with selectors discovered by recording real user interaction with `invoke playwright-record`.

**Impact:** `beacon_scraper.py` fully rewritten.  Config keys `members_export_url` and `groups_export_url` replaced by `members_link_name` and `groups_link_name`.  Confirmed values for Petersfield U3A: `Members and addresses` / `Groups, with members, venues`.  `scripts/` added to `.gitignore` because recorded scripts contain plaintext credentials.

**Follow-up:** If Beacon changes its login layout, re-run `invoke playwright-record` and update selectors.

---

## 2026-04-27 — SQLite Staging Layer Added

**Decision:** An optional SQLite staging step (`database.py`) has been inserted between Excel parsing and WordPress mapping.

**Rationale:** The Beacon download takes meaningful time (~30 seconds) and produces fixed snapshots.  Staging to SQLite allows the same snapshot to be reprocessed for multiple output targets (WordPress, reporting, analysis) without repeating the download.  This also provides an audit trail and a convenient inspection point.

**Impact:** New module `database.py` with `init_database`, `store_records`, and `clear_records`.  New `[database]` config section with `enabled`, `path`, and `persist_across_sessions` keys.  `sync.py` orchestrates clear→store when enabled.  `state.json` now includes a `staged` metric.

**Follow-up:** Query `state/beacon_data.db` with any SQLite browser for ad-hoc analysis.  Consider adding a CLI sub-command to inspect staged records.

---

## 2026-04-27 — Database Persistence Policy

**Decision:** The default persistence mode is `persist_across_sessions = false` — the staging table is cleared before each sync run.

**Rationale:** Safe by default: operators always see only the current run's data when querying the database.  Avoids silent row accumulation that could mislead analysis.  Persistent mode (`true`) is available for explicit historical trending use cases.

**Impact:** `sync.py` calls `clear_records()` before `store_records()` unless `persist_across_sessions` is truthy.  Both modes have dedicated integration tests.

**Follow-up:** If historical trending is needed, set `persist_across_sessions = true` and implement a periodic archival/pruning strategy.

---

## 2026-04-28 — SQLite Schema: Workbook-Driven (Option 1)

**Decision:** `database.py` was redesigned from a single `staged_records` table (with JSON blob per record) to a workbook-driven schema where each Excel sheet becomes its own SQLite table.

**Rationale:** The JSON-blob approach made ad-hoc querying cumbersome and required a separate schema config. The sheet-per-table design is schema-free (headers drive column names), supports SQL queries directly on native field values, and handles both workbooks uniformly without any additional configuration.

**Impact:** `load_workbook_to_db(db_path, workbook_path, *, append=False)` replaces `init_database`, `store_records`, and `clear_records`. Each table has `_id` (autoincrement PK) and `_staged_at` (timestamp) prepended. Live workbooks produce 7 tables: `members`, `polls`, `groups`, `group_members`, `venues`, `faculties`, `group_ledgers`. All 16 database tests updated.

**Follow-up:** Inspect tables with any SQLite browser; column names match the Excel headers verbatim after sanitisation.

---

## 2026-04-28 — New CLI Tasks: beacon-sqlite-dry-run and export-member-names

**Decision:** Two new CLI subcommands added alongside the existing `sync` command.

**Rationale:** Users need to validate the download pipeline independently of WordPress, and to export specific data slices (e.g. member names for a mailing list) without running the full sync. Independent tasks reduce risk and shorten feedback loops.

**Impact:**
- `beacon-sqlite-dry-run [--db-path PATH]` — downloads and stages all workbook sheets to SQLite; no WordPress interaction.
- `export-member-names [--output-dir PATH]` — downloads Members export and writes `Member_Names.xlsx` (worksheet: *Member Names*; columns: `mem_no`, `status`, `title`, `forename`, `surname`). Live run: 1,815 rows written.
- `sync.py` gains `run_beacon_to_sqlite_dry_run` and `run_export_member_names`; shared `_stage_exports_to_db` helper.
- `cli.py` gains two new subparsers with optional path overrides.

**Follow-up:** Consider additional export targets (e.g. Groups summary) as further independent tasks.

---

## 2026-04-28 — output_dir Config Parameter

**Decision:** The output directory for file exports is now configurable via `beacon_export.output_dir` in `config.ini`, with a `--output-dir` CLI override per command.

**Rationale:** Hard-coding an output directory reduces flexibility. Config-first with CLI override follows the same pattern used for other path settings and avoids environment-specific paths in source code.

**Impact:** `config/config.ini` and `config/config.example.ini` updated with `output_dir = outputs` under `[beacon_export]`. `export-member-names` resolves the output directory in order: CLI flag → config value → exit 1 with a clear error.

**Follow-up:** Apply the same config-first pattern to any future export commands.