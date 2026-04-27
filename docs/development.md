# Development

![U3A Logo](img/u3a-logo.png){style="float: right; max-width: 180px; height: auto; margin: -4.5rem 0 0.5rem 1rem;"}

## Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS
pip install -e .[dev]
python -m playwright install chromium
copy config\config.example.ini config\config.ini
```

Edit `config/config.ini` with your Beacon credentials and WordPress application password.
Never commit `config.ini` to version control.

## Task Runner

All common workflows are managed via `invoke`:

| Command | Purpose |
|---|---|
| `python -m invoke deps` | Sync dependencies from pyproject.toml |
| `python -m invoke docs` | Start MkDocs live server (port 8020) |
| `python -m invoke build` | Build wheel and docs |
| `python -m invoke bump --part=patch` | Bump patch version |
| `python -m invoke bump --part=minor` | Bump minor version |
| `python -m invoke playwright-record` | Record Beacon interactions (use to discover export URLs) |
| `python -m invoke ci` | Run local CI: build + tests with >80% coverage gate |

## Tests

Run the full test suite with coverage:

```bash
python -m pytest -q --cov=beaconutilities --cov-report=term-missing
```

### Coverage Gate

CI enforces **>80% overall unit test coverage**. Running `invoke ci` will fail if coverage drops below this threshold.

Test files and their coverage targets:

| Test file | Module(s) covered | Target |
|---|---|---|
| `test_config.py` | `config.py` | 90%+ |
| `test_models.py` | `models.py` | 100% |
| `test_excel_parser.py` | `excel_parser.py` | 90%+ |
| `test_mapping.py` | `mapping.py` | 90%+ |
| `test_preflight.py` | `preflight.py` | 90%+ |
| `test_wordpress.py` | `wordpress.py` | 85%+ |
| `test_sync.py` | `sync.py` | 85%+ |
| `test_cli.py` | `cli.py` | 80%+ |

## Definition of Done

A change is not complete until **all** of the following are true:

- [ ] Tests added or updated; CI passes with >80% coverage
- [ ] `docs/overview.md` updated if scope or workflow changed
- [ ] `docs/architecture.md` updated if new modules or boundaries changed
- [ ] `docs/development.md` updated if developer workflow or commands changed
- [ ] `docs/user_docs/` updated if user-facing behaviour changed
- [ ] `docs/Appendices/1_DevelopmentNotes.md` updated with any new decisions
- [ ] `docs/Appendices/2_DevelopmentProgress.md` updated with milestone entry
- [ ] `invoke docs` builds cleanly with no broken links

## Versioning

Version is maintained in `src/beaconutilities/__init__.py` and `pyproject.toml`. Use `invoke bump` to update both together.

Version progression:

| Version | Milestone |
|---|---|
| 0.0.x | Scaffolding and PoC development |
| 0.1.0 | Phase I PoC complete (Members + Groups, Beacon → WordPress) |
| 1.0.0 | Production-ready, operations-validated release |
