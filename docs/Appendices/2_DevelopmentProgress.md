# Appendix 2: Development Progress

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix tracks milestone-by-milestone progress.  A new row is added at the start of each sprint or significant work session.  Evidence links point to files, test results, or screenshots that demonstrate completion.

| Date | Version | Milestone | Status | Scope | Evidence | Docs Updated |
|------|---------|-----------|--------|-------|----------|--------------|
| 2026-04-27 | 0.0.1 | Initial project scaffold | Complete | Project structure, config, logging, state, stub CLI | Repository created | overview, architecture, development, operations |
| 2026-04-27 | 0.0.1 | Phase I planning | Complete | Scope locked: Members + Groups, Beacon to WordPress, >80% coverage gate | Session plan in /memories/session/plan.md | Appendix 1, Appendix 2 |
| 2026-04-27 | 0.0.1 | Phase I implementation - core modules | Complete | excel_parser, models, beacon_scraper, wordpress, mapping, sync, preflight, cli updated | All source files in src/beaconutilities/ | overview, architecture, development, operations, Appendix 1 |
| 2026-04-27 | 0.0.1 | Phase I implementation - unit tests | Complete | test_models, test_excel_parser, test_mapping, test_preflight, test_wordpress, test_sync, test_cli | tests/ directory | development.md coverage table |
| 2026-04-27 | 0.0.1 | CI quality gate | Complete | >80% coverage enforced in tasks.py and pyproject.toml | tasks.py, pyproject.toml | development.md |
| 2026-04-27 | 0.0.1 | Playwright recording — members | Complete | Confirmed login flow, Select2 site picker, named export links | scripts/members_download.py (gitignored) | Appendix 1, Appendix 3, beacon_scraper.py |
| 2026-04-27 | 0.0.1 | Playwright recording — groups | Complete | Confirmed groups export link name; beacon_scraper.py fully rewritten | scripts/groups_download.py (gitignored) | Appendix 1, Appendix 3, config.example.ini |
| 2026-04-27 | 0.0.1 | Live download validation | Complete | members.xlsx 333,407 bytes; groups.xlsx 91,090 bytes downloaded successfully | downloads/ directory (gitignored) | overview.md |
| 2026-04-27 | 0.0.1 | SQLite staging layer | Complete | database.py with init_database, store_records, clear_records; configurable persist_across_sessions | src/beaconutilities/database.py, tests/test_database.py | architecture.md, operations.md, Appendix 1 |
| 2026-04-27 | 0.0.1 | Dry-run PoC demonstration | Complete | 3,242 members + 1,382 groups staged = 4,624 records; no WordPress writes | CLI log output confirmed | overview.md |
| 2026-04-28 | 0.0.3 | SQLite schema redesigned — workbook-driven | Complete | database.py rewritten; each Excel sheet → its own table; 7 tables from 2 workbooks; old staged_records table removed | src/beaconutilities/database.py, tests/test_database.py (16 tests) | architecture.md, operations.md, Appendix 1 |
| 2026-04-28 | 0.0.3 | New CLI tasks: beacon-sqlite-dry-run, export-member-names | Complete | Two independent task subcommands added; run_beacon_to_sqlite_dry_run and run_export_member_names in sync.py | src/beaconutilities/cli.py, src/beaconutilities/sync.py, tests/test_cli.py, tests/test_sync.py | architecture.md, operations.md, user-guide.md, Appendix 1 |
| 2026-04-28 | 0.0.3 | output_dir config parameter | Complete | beacon_export.output_dir in config.ini; CLI --output-dir override; clear error if neither set | config/config.example.ini, cli.py | architecture.md, operations.md, Appendix 1 |
| 2026-04-28 | 0.0.3 | Live Member_Names.xlsx generated | Complete | 1,815 rows; worksheet "Member Names"; columns: mem_no, status, title, forename, surname | outputs/Member_Names.xlsx (gitignored) | overview.md |
| — | 0.0.x | Excel column header inspection | Pending | Confirm field names in mapping.py constants against actual export headers; store fixtures | tests/fixtures/members.xlsx, tests/fixtures/groups.xlsx | mapping.py, architecture.md |
| — | 0.1.0 | Phase I PoC complete | Pending | Controlled publish to staging WordPress; Member and Group content visible | WordPress staging screenshots | overview, user-guide, Appendix 5 |