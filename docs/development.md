# Development

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e .[dev]
python -m playwright install chromium
copy config\config.example.ini config\config.ini
```

## Task Runner

All common workflows are managed via `invoke`:

| Command | Purpose |
|---|---|
| `python -m invoke deps` | Sync dependencies from pyproject.toml |
| `python -m invoke docs` | Start MkDocs live server |
| `python -m invoke build` | Build wheel and docs |
| `python -m invoke bump --part=patch` | Bump patch version |
| `python -m invoke bump --part=minor` | Bump minor version |
| `python -m invoke playwright-record` | Record Beacon interactions |
| `python -m invoke ci` | Run local CI (build + tests) |

## Tests

```bash
python -m pytest -q
```

## Versioning

Version is maintained in `src/beaconutilities/__init__.py` and `pyproject.toml`. Use `invoke bump` to update both together.
