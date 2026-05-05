# Installation Guide

![U3A Logo](../img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Prerequisites

- Python 3.11 or later
- Internet access

## End-User Installer (Recommended)

### Recommended install location

- Keep the downloaded installer zip in your normal Downloads folder.
- Extract `BeaconUtilities` into a user-owned documents/work folder.
- Avoid protected folders such as `Program Files`, `C:\Windows`, `/Applications`, or system directories that may require admin rights.

Suggested locations:

- Windows: `C:\Users\<your-user>\Documents\BeaconUtilities`
- macOS: `/Users/<your-user>/Documents/BeaconUtilities`
- Linux: `/home/<your-user>/BeaconUtilities`

1. Download and extract the latest installer zip, then open the extracted `BeaconUtilities` folder.

2. Run the installer script for your platform:

    Windows:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -InstallChromium
    ```

    macOS / Linux:

    ```bash
    bash ./install.sh --install-chromium
    ```

3. Configure Beacon and WordPress:

    The installer creates `config/config.ini` from `config.example.ini` if needed.
    See [Appendix 6: Configuration Reference](../Appendices/6_ConfigurationReference.md) for a full description of each configuration key.

    Edit `config/config.ini`. Required sections:

    | Section | Key fields |
    | ------- | ---------- |
    | `[beacon]` | `portal_url`, `site_name`, `username`, `password` |
    | `[beacon_export]` | `members_link_name`, `groups_link_name`, `backup_section_link_name`, `backup_download_link_name`, `download_dir`, `backup_output_dir` |
    | `[wordpress]` | `site_url`, `username`, `application_password` |

4. Verify installation:

    Windows:

    ```powershell
    .\run.ps1 --help
    ```

    macOS / Linux:

    ```bash
    ./run.sh --help
    ```

5. Test with a dry run:

    Windows:

    ```powershell
    .\run.ps1 sync --dry-run
    ```

    macOS / Linux:

    ```bash
    ./run.sh sync --dry-run
    ```

    Inspect the log output at `logs/beacon_utilities.log` before your first live run.

6. Run normal operations with the launcher script:

    Windows:

    ```powershell
    .\run.ps1 sync
    ```

    macOS / Linux:

    ```bash
    ./run.sh sync
    ```

7. Start user docs locally using the launcher script created by install:

    Windows:

    ```powershell
    .\start-user-docs.ps1
    ```

    macOS / Linux:

    ```bash
    ./start-user-docs.sh
    ```

    Opens `docs/index.html` directly in the default browser. Falls back to
    `https://petersfieldu3a.github.io/BeaconUtilities/` if the local docs folder is not present.

    Windows (double-clickable): `start-user-docs.cmd`

8. Run full Beacon backup using the launcher script created by install:

    Windows:

    ```powershell
    .\start-beacon-backup.ps1
    ```

    macOS / Linux:

    ```bash
    ./start-beacon-backup.sh
    ```

    By default the backup is saved in `beacon_export.backup_output_dir` using a Beacon-style timestamped file name such as `202604281322_Petersfield u3abackup.xlsx`.

    Optional output path override:

    ```text
    Windows: .\start-beacon-backup.ps1 C:\Backups
    Windows (double-clickable): start-beacon-backup.cmd
    macOS / Linux: ./start-beacon-backup.sh /tmp/backups
    ```

    Pass a full `.xlsx` path only when you want to force an exact file name.

## Developer Setup (From Source)

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

    Edit `config\config.ini`. Required sections:

    | Section | Key fields |
    | ------- | ---------- |
    | `[beacon]` | `portal_url`, `site_name`, `username`, `password` |
    | `[beacon_export]` | `members_link_name`, `groups_link_name`, `backup_section_link_name`, `backup_download_link_name`, `download_dir`, `backup_output_dir` |
    | `[wordpress]` | `site_url`, `username`, `application_password` |

5. Discover Beacon export link names:

    The `members_link_name` and `groups_link_name` values are specific to your Beacon organisation. The full-backup flow can use a different Beacon menu option, so confirm `backup_section_link_name` and `backup_download_link_name` as well. Use the recording tool to find them:

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
