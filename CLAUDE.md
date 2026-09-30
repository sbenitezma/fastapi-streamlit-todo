# CLAUDE.md

Context for Claude Code sessions in this repo. The README is the user-facing
reference; this file holds what an assistant needs to work here without guessing.

## Project

Task manager in two processes that only talk over HTTP:

- `api/` — FastAPI + stdlib `sqlite3` (no ORM). Layers: `database.py` (engine)
  → `todos_service.py` (`TodoRepository` = all SQL, `TodoService` = business
  rules) → `routes.py` (Pydantic validation, `Depends`) → `main.py` (maps domain
  errors to 404/400).
- `frontend/` — Streamlit dashboard, package `dashboard`. `api_client.py` is the
  only I/O module; `formatting`, `tasks`, `filtering` are pure and unit-tested;
  `components/` is the internal UI library, browsed via `component_library.py`.

The dashboard never imports `sqlite3` or anything from `api/`. Keep it that way.

## Commands

Everything runs in Docker; the host does not need the project's dependencies.

| Task | Windows | macOS / Linux |
|---|---|---|
| Lint (ruff check + format check + mypy) | `.\run.ps1 lint` | `make lint` |
| Tests (pytest + coverage gate) | `.\run.ps1 test` | `make test` |
| Start API :8000 + dashboard :8501 | `.\run.ps1 start` | `make start` |
| Component library :8502 | `.\run.ps1 library` | `make library` |

`/ci-local` runs the lint + test pair, the same checks as `.github/workflows/ci.yml`.

## Rules that CI enforces

- Python 3.12 (`requires-python`, Docker image, CI). The host interpreter may be
  newer: don't use syntax or stdlib APIs newer than 3.12.
- ruff config in `pyproject.toml`. A PostToolUse hook (`.claude/hooks/ruff_on_edit.py`)
  fixes and formats each edited `.py` with the ruff version pinned in
  `requirements-dev.txt`, installing it into `.claude/.tools/` when the pin changes.
- mypy covers `api/` only.
- Coverage of `api/` must stay ≥ 90 %. New API behaviour needs tests in `tests/`
  (endpoint tests in `test_todos.py`, service/repository tests in
  `test_todos_service.py`); each test gets its own temp SQLite file from `conftest.py`.
- Dependencies are pinned in `requirements*.txt` and bumped by Dependabot.

## Conventions

- All SQL lives in `TodoRepository`, parameterised. The service and repository
  don't import FastAPI.
- Components follow `frontend/dashboard/components/README.md` (positional data,
  keyword-only options, required `key` for widgets, colour never carries meaning
  alone). New component → `/new-component`.
- Streamlit APIs change between minor versions: check the docs for the pinned
  version before using a widget or parameter (e.g. `st.iframe`, not the
  deprecated `components.html`).
- Commits follow Conventional Commits (`feat(api):`, `fix(web):`, `test(frontend):`,
  `ci:`, `docs:` …), one logical change per PR.

## Security scope

Single-user, local tool with no authentication. Ports are published on
`127.0.0.1` only and the non-Docker entry points bind to loopback; don't change
that without adding auth first (see README → Security & scope).
