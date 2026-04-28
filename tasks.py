"""Invoke task definitions for development, build, and release workflows."""

from __future__ import annotations

from datetime import date
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from invoke import task

__version__ = "0.0.4"
__author__ = "T. J. Willans"
__date__ = "2026-04-28"
__copyright__ = "Copyright 2026, MEADC Ltd"

ROOT = Path(__file__).resolve().parent
PACKAGE_INIT = ROOT / "src" / "beaconutilities" / "__init__.py"
PYPROJECT = ROOT / "pyproject.toml"
PYTHON = f'"{sys.executable}"'


def _read_version() -> str:
    text = PACKAGE_INIT.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', text)
    if not match:
        raise ValueError("Could not find __version__ in package __init__.py")
    return match.group(1)


def _bump_version(current: str, part: str) -> str:
    major, minor, patch = [int(x) for x in current.split(".")]
    if part == "major":
        return f"{major + 1}.0.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.{patch + 1}"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("part must be one of: major, minor, patch")


def _update_release_metadata(path: Path, version: str, release_date: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text

    if path.name == "pyproject.toml":
        updated = re.sub(
            r'(?m)^version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"$',
            f'version = "{version}"',
            updated,
            count=1,
        )
    else:
        updated = re.sub(
            r'(?m)^__version__\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"$',
            f'__version__ = "{version}"',
            updated,
            count=1,
        )
        updated = re.sub(
            r'(?m)^__date__\s*=\s*"[0-9]{4}-[0-9]{2}-[0-9]{2}"$',
            f'__date__ = "{release_date}"',
            updated,
            count=1,
        )

    if updated != text:
        path.write_text(updated, encoding="utf-8")


def _changed_python_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "*.py"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        return []
    changed = []
    for rel in proc.stdout.splitlines():
        rel_path = Path(rel)
        if rel_path.suffix == ".py":
            changed.append(ROOT / rel_path)
    return changed


def _parse_version(filename: str) -> tuple[int, int, int] | None:
    match = re.search(r'-(\d+)\.(\d+)\.(\d+)', filename)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None


@task
def docs(c):
    """Start MkDocs live server."""
    c.run(f"{PYTHON} -m mkdocs serve --livereload --dev-addr 127.0.0.1:8020", pty=False)


@task
def build(c):
    """Build package artifacts (wheel + docs)."""
    c.run(f"{PYTHON} -m build", pty=False)
    c.run(f"{PYTHON} -m mkdocs build", pty=False)

    dist_dir = ROOT / "dist"
    version = _read_version()

    # Cleanup old builds, keeping only 3 most recent versions
    patterns = [
        'beacon_utilities-*.tar.gz',
        'beacon_utilities-*-py3-none-any.whl',
    ]
    for pattern in patterns:
        files = list(dist_dir.glob(pattern))
        if files:
            files.sort(key=lambda p: _parse_version(p.name) or (0, 0, 0), reverse=True)
            for old in files[3:]:
                old.unlink()
                print(f"Removed old build: {old.name}")


@task
def deps(c, dev=True):
    """Install dependencies from pyproject.toml into the active environment."""
    c.run(f"{PYTHON} -m pip install --upgrade pip", pty=False)
    if dev:
        c.run(f'{PYTHON} -m pip install -e ".[dev]"', pty=False)
    else:
        c.run(f"{PYTHON} -m pip install -e .", pty=False)


@task
def playwright_install(c, browser="chromium"):
    """Install Playwright browser binaries (outside Python package dependencies)."""
    c.run(f"{PYTHON} -m playwright install {browser}", pty=False)


@task
def playwright_record(
    c,
    browser="chromium",
    target="https://www.u3abeacon.org.uk/",
    output="",
):
    """Launch Playwright codegen for recording Beacon portal interactions."""
    output_arg = f' --output "{output}"' if output else ""
    c.run(
        f'{PYTHON} -m playwright codegen --browser {browser}{output_arg} "{target}"',
        pty=False,
    )


@task
def bump(c, part="patch"):
    """Bump package version and update release metadata on changed Python files."""
    current = _read_version()
    new_version = _bump_version(current, part)
    release_date = date.today().isoformat()

    _update_release_metadata(PACKAGE_INIT, new_version, release_date)
    _update_release_metadata(PYPROJECT, new_version, release_date)

    for script in _changed_python_files():
        _update_release_metadata(script, new_version, release_date)

    print(f"Version bumped: {current} -> {new_version} ({release_date})")


@task(pre=[build])
def ci(c):
    """Run local CI subset: build, then tests with coverage gate (>80%)."""
    c.run(f"{PYTHON} -m pytest -q --cov=src/beaconutilities --cov-report=term-missing --cov-fail-under=80", pty=False, warn=False)


@task
def package(c):
    """Build user-docs and create dist/beacon_utilities-{version}.zip installer package."""
    version = _read_version()
    archive_root = Path("BeaconUtilities")

    # Build user-facing docs
    c.run(f"{PYTHON} -m mkdocs build -f mkdocs-user.yml", pty=False)

    # Build wheel only (no sdist needed in installer)
    c.run(f"{PYTHON} -m build --wheel", pty=False)

    dist_dir = ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)

    zip_path = dist_dir / f"beacon_utilities-{version}.zip"

    wheel_glob = list(dist_dir.glob(f"beacon_utilities-{version}-*.whl"))
    if not wheel_glob:
        raise FileNotFoundError(f"No wheel found in dist/ for version {version}")
    wheel_path = wheel_glob[0]

    site_dir = ROOT / "site_installer"
    config_example_ini = ROOT / "config" / "config.example.ini"
    config_example_json = ROOT / "config" / "config.example.json"
    installer_script = ROOT / "installer" / "install.ps1"
    installer_script_unix = ROOT / "installer" / "install.sh"
    launcher_script = ROOT / "installer" / "run.ps1"
    launcher_script_unix = ROOT / "installer" / "run.sh"
    installer_readme = ROOT / "installer" / "INSTALL.txt"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(wheel_path, archive_root / wheel_path.name)

        for installer_file in (
            installer_script,
            installer_script_unix,
            launcher_script,
            launcher_script_unix,
            installer_readme,
        ):
            if installer_file.exists():
                zf.write(installer_file, archive_root / installer_file.name)

        for doc_file in sorted(site_dir.rglob("*")):
            if doc_file.is_file():
                zf.write(
                    doc_file,
                    archive_root / "docs" / doc_file.relative_to(site_dir),
                )

        for cfg in (config_example_ini, config_example_json):
            if cfg.exists():
                zf.write(cfg, archive_root / "config" / cfg.name)

    print(f"Installer package created: {zip_path}")
