# Operations

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

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
- A successful run ends with `Sync result: {'status': ...}`.

## Safe Operations

- Always run `--dry-run` (when implemented) before live runs after config changes.
- Do not delete `state/state.json` unless you understand the recovery impact.
- Keep one person responsible for approving any browser challenge during scheduled windows.
