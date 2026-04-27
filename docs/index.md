# BeaconUtilities { style="margin-top: 0.0rem; padding-top: 0;" }

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

BeaconUtilities is a Python-based automation tool that accesses [Beacon](https://www.u3abeacon.org.uk/), the U3A CRM, via Playwright browser automation and uses the data to populate pages on the Petersfield U3A WordPress website.

## Project Focus

- Playwright-driven automation of Beacon CRM (no public API available).
- INI-backed configuration and JSON-backed runtime state.
- WordPress REST API integration for automated page/post updates.

## End Users

If you are operating the tool (rather than developing it), start with [User Guide](user_docs/user-guide.md) and [Installation Guide](user_docs/installation.md).

## Full Scope

See [overview.md](overview.md) for the complete project scope and architecture.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -e .[dev]
copy config\config.example.ini config\config.ini
beacon-utilities --help
```
