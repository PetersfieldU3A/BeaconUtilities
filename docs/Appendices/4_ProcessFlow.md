# Appendix 4: Application Process Flow

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix summarises the current runtime command flows implemented by BeaconUtilities.

## Diagram 1: Command Overview

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}}}%%
graph TD
    A[Start command] --> B[Load config.ini]
    B --> C{Command}
    C -->|sync| D[Run Beacon to WordPress sync]
    C -->|beacon-sqlite-dry-run| E[Download Beacon exports and stage to SQLite]
    C -->|export-member-names| F[Download Members export and write Member_Names.xlsx]
    C -->|backup-beacon| G[Download full Beacon backup workbook]
    D --> H[End]
    E --> H
    F --> H
    G --> H
```

## Diagram 2: Sync Flow

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}}}%%
graph TD
    A[Start sync] --> B[Load config.ini]
    B --> C[Preflight Beacon config]
    C --> D{Dry run?}
    D -->|No| E[Preflight WordPress config]
    D -->|Yes| F[Login to Beacon via Playwright]
    E --> F
    F --> G[Download Members and Groups workbooks]
    G --> H[Parse workbook sheets into BeaconRecord items]
    H --> I{SQLite enabled?}
    I -->|Yes| J[Load all sheets into SQLite]
    I -->|No| K[Map records to WordPress payloads]
    J --> K
    K --> L{Dry run?}
    L -->|Yes| M[Log mapped results only]
    L -->|No| N[Upsert records to WordPress]
    M --> O[Return result without updating state]
    N --> P[Write state/state.json]
    O --> Q[End]
    P --> Q
```

## Diagram 3: Utility Export Flows

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}}}%%
graph TD
    A[Start utility command] --> B{Command}
    B -->|beacon-sqlite-dry-run| C[Preflight Beacon config]
    B -->|export-member-names| D[Preflight Beacon config]
    B -->|backup-beacon| E[Preflight Beacon backup config]

    C --> F[Download Members and Groups workbooks]
    F --> G[Load all sheets into SQLite]
    G --> H[Return row and table counts]

    D --> I[Download Members workbook]
    I --> J[Read Members sheet]
    J --> K[Write Member_Names.xlsx]
    K --> L[Return output path and row count]

    E --> M[Login to Beacon via Playwright]
    M --> N[Open configured backup section]
    N --> O[Click configured backup download link]
    O --> P[Save workbook to backup_output_dir]
    P --> Q[Use timestamped Beacon-style file name unless explicit .xlsx path supplied]
    Q --> R[Return output path]
```

## Notes

- The `sync` command is the only path that publishes to WordPress.
- The `beacon-sqlite-dry-run`, `export-member-names`, and `backup-beacon` commands do not update WordPress.
- The `backup-beacon` command does not stage data to SQLite or update `state/state.json`.
- Default backup naming follows the Beacon-style pattern `YYYYMMDDHHMM_<site_name> u3abackup.xlsx`.
