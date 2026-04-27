# Installation Guide

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Prerequisites

- Python 3.11 or later
- Git
- Internet access

## Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/PetersfieldU3A/BeaconUtilities.git
    cd BeaconUtilities
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    .venv\Scripts\activate       # Windows
    # source .venv/bin/activate  # macOS / Linux
    ```

3. Install dependencies:

    Dependencies include `requests`, `playwright`, and `openpyxl` (for parsing Beacon Excel exports), plus development tools.

    ```bash
    pip install -e .[dev]
    python -m playwright install chromium
    ```

4. Configure Beacon and WordPress:

    ```bash
    copy config\config.example.ini config\config.ini
    ```

    Edit `config\config.ini`.  Required sections:

    | Section | Key fields |
    |---------|------------|
    | `[beacon]` | `portal_url`, `username`, `password` |
    | `[beacon_export]` | `members_export_url`, `groups_export_url`, `download_dir` |
    | `[wordpress]` | `site_url`, `username`, `application_password` |

5. Discover Beacon export URLs:

    The `members_export_url` and `groups_export_url` values are specific to your Beacon organisation.  Use the recording tool to find them:

    ```bash
    python -m invoke playwright-record
    ```

    A browser window will open.  Navigate to the Members or Groups export page and copy the URL from the address bar into `config\config.ini`.

6. Verify installation:

    ```bash
    beacon-utilities --help
    ```

7. Test with a dry run:

    ```bash
    .venv\Scripts\python.exe -m beaconutilities.cli sync --dry-run
    ```

    Inspect the log output at `logs/beacon_utilities.log` to confirm extraction and mapping work correctly before committing to a live run.
