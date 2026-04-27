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

    ```bash
    pip install -e .[dev]
    python -m playwright install chromium
    ```

4. Configure:

    ```bash
    copy config\config.example.ini config\config.ini
    ```

    Edit `config\config.ini` with your Beacon credentials and WordPress API details.

5. Verify:

    ```bash
    beacon-utilities --help
    ```
