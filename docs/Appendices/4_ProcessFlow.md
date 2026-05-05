# Appendix 4: Application Process Flow

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

This appendix summarises the current runtime command flows implemented by BeaconUtilities.
Diagram labels are intentionally concise and rendered at a larger base font for readability.

## Diagram 1: Command Overview

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}}}%%
graph TD
    A[Start command] --> B[Load config.ini]
    B --> C{Command}
    C -->|sync| D[Beacon to WordPress sync]
    C -->|beacon-sqlite-dry-run| E[Beacon exports to SQLite]
    C -->|export-member-names| F[Write Member_Names.xlsx]
    C -->|export-group-data| G[Write Group_Data.xlsx]
    C -->|backup-beacon| H[Download full backup workbook]
    D --> I[End]
    E --> I
    F --> I
    G --> I
    H --> I
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
    B -->|export-group-data| E[Preflight Beacon config]
    B -->|backup-beacon| F[Preflight Beacon backup config]

    C --> G[Download Members and Groups workbooks]
    G --> H[Load all sheets into SQLite]
    H --> I[Return row and table counts]

    D --> J[Download Members workbook]
    J --> K[Read Members sheet]
    K --> L[Write Member_Names.xlsx]
    L --> M[Return output path and row count]

    E --> N[Download Groups workbook]
    N --> O[Read Groups sheet]
    O --> P[Write Group_Data.xlsx]
    P --> Q[Return output path and row count]

    F --> R[Login to Beacon via Playwright]
    R --> S[Open configured backup section]
    S --> T[Click configured backup download link]
    T --> U[Save workbook to backup_output_dir]
    U --> V[Use timestamped Beacon-style name unless explicit .xlsx path is supplied]
    V --> W[Return output path]
```

## Notes

- The `sync` command is the only path that publishes to WordPress.
- The `beacon-sqlite-dry-run`, `export-member-names`, `export-group-data`, and `backup-beacon` commands do not update WordPress.
- The `backup-beacon` command does not stage data to SQLite or update `state/state.json`.
- The `export-group-data` command writes only the Groups sheet rows to `Group_Data.xlsx`.
- Default backup naming follows the Beacon-style pattern `YYYYMMDDHHMM_<site_name> u3abackup.xlsx`.
