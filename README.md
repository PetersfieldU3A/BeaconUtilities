# BeaconUtilities

Programmatic access to [Beacon](https://www.u3abeacon.org.uk/), the U3A CRM, via Playwright browser automation.

As Beacon does not provide a user-accessible API, Playwright is used to mimic user interaction. Once interaction with Beacon has been proven the main aim is to automatically populate pages on the Petersfield U3A WordPress website.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -e .[dev]
copy config\config.example.ini config\config.ini
beacon-utilities --help
```

## Documentation

Full documentation is built with MkDocs:

```bash
python -m invoke docs
```

## Development

See [docs/development.md](docs/development.md) for conventions and workflow.

## License

Copyright 2026, MEADC Ltd
