# Architecture

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Package Structure

```
src/beaconutilities/
    __init__.py       Package metadata and version
    cli.py            Command line entrypoint
    config.py         INI/JSON configuration loader
    logging_utils.py  Rotating file + console logging
    models.py         Data models (BeaconRecord, etc.)
    mapping.py        Beacon → WordPress field mapping
    preflight.py      Pre-run validation checks
    state.py          JSON-backed runtime state
    sync.py           Sync orchestration
```

## Configuration

Runtime configuration is stored in `config/config.ini` (gitignored). A template is provided at `config/config.example.ini`.

## State

Run state is persisted as JSON in `state/state.json` (gitignored). This allows resumable and auditable operation.

## Logging

Rotating log files are written to `logs/beacon_utilities.log` (gitignored). Up to 5 backups are retained at ~1 MB each.
