# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Opens at `http://localhost:8000`. The SQLite database (`raci_vs.db`) is created automatically on first run.

No build step, no Node.js, no frontend compilation.

## Architecture

**Stack:** FastAPI + SQLAlchemy + Jinja2 + HTMX + PicoCSS + python-docx. Pure server-rendered HTML with HTMX partial swaps — no JavaScript framework.

**Multi-organisation scoping:** Every `Function` and `Task` row has an `organisation_id` foreign key. The active organisation is carried as a cookie (`current_org_id`) and resolved on every request by `get_org_context` in [dependencies.py](dependencies.py), which is injected as a FastAPI dependency. All queries must filter by `current_org_id`.

**Request flow:**
1. FastAPI route receives request
2. `get_db()` yields a fresh SQLAlchemy session (closed in `finally`)
3. `get_org_context()` resolves the active org from the cookie
4. Route queries the DB, renders a Jinja2 template, returns HTML
5. HTMX swaps only the relevant fragment; full reloads are avoided

**Key models** ([models.py](models.py)):
- `Organisation` — top-level tenant; all data is isolated per org
- `Function` — an organisational role; self-referential `parent_id` and `emergency_rep_id`
- `Task` — a work item or activity
- `FunctionTaskRole` — junction table linking a function to a task; unique constraint on `(function_id, task_id)`; `role` is one of `R A C I V S`; `r_subcategory` is only populated when `role = 'R'`

**Role validation** lives in `validate_role()` in [models.py](models.py) and is called by every assignment endpoint. Role R requires a subcategory; all other roles get `r_subcategory = NULL`.

**Document generation** ([services/docx_generator.py](services/docx_generator.py)): builds `.docx` entirely in-memory via `python-docx`, returns a `BytesIO` buffer — nothing written to disk.

**Schema migrations** run at startup in [main.py](main.py) before `Base.metadata.create_all`. New columns use `ALTER TABLE … ADD COLUMN` wrapped in try/except. Structural changes (e.g. dropping a unique constraint) rebuild the table via create-copy-drop-rename. Fresh installs skip all migrations.

**Routers** ([routers/](routers/)):
- `functions.py` — Function CRUD (org-scoped)
- `tasks.py` — Task CRUD (org-scoped)
- `assignments.py` — create/delete `FunctionTaskRole` entries; returns HTMX partials
- `documents.py` — HTML preview and `.docx` download endpoints
- `organisations.py` — export (JSON) and import endpoints

## Branches

| Branch | Purpose |
|---|---|
| `master` | Main branch — SQLite-backed, runs locally with `uvicorn` |
| `feature/azure-sql-backend` | Replaces SQLite with Azure SQL Server; `DATABASE_URL` is read from an `.env` file via `python-dotenv`; `pyodbc` added to requirements |
| `feature/desktop-app` | Windows desktop packaging via PyInstaller; `launcher.py` starts uvicorn in a background thread, opens the browser, and keeps a system-tray icon (`pystray`); build with `build.bat`; Inno Setup script (`raci_vs.iss`) produces `Setup.exe`; GitHub Actions workflow publishes the installer automatically on release |

### feature/azure-sql-backend

Set `DATABASE_URL` in a `.env` file:
```
DATABASE_URL=mssql+pyodbc://<user>:<pass>@<server>/<db>?driver=ODBC+Driver+18+for+SQL+Server
```
Omitting it falls back to SQLite.

### feature/desktop-app

Development run (no build needed):
```bash
python launcher.py
```

Build the `.exe`:
```bash
build.bat
# output: dist\RACI-VS\RACI-VS.exe
# then open raci_vs.iss in Inno Setup Compiler for the installer
```
