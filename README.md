# RACI-VS Matrix Manager

A locally-running web app for managing RACI-VS responsibility matrices across company functions and tasks, with Word document export. Supports multiple independent organisations in a single database.

## Features

- **Multi-organisation support** — create any number of named organisations; each has its own isolated set of functions, tasks, and assignments. Switch between them from the nav bar; new organisations start completely empty.
- **Function management** — create functions with company hierarchy, description, aim, and emergency representative
- **Task management** — create tasks with descriptions and assign functions to them with RACI-VS roles
- **R-role subcategory** — Responsible (R) assignments carry one of five subcategories (Ausführende Tätigkeit, Gewährleistung, Koordination, Veranlassung, Mitwirkung); visible in the function document, not in the matrix
- **Matrix view** — live overview table: tasks as rows, functions as columns, with colour-coded role badges
- **Organisation chart** — visual top-down hierarchy diagram of all functions in the active organisation, based on parent-function relationships
- **Interface analysis** — select any two functions to see the tasks they share and their respective roles
- **Document preview & export** — view function descriptions, task descriptions, and interface reports directly in the browser as a formatted HTML page (opens in a new tab); download as `.docx` for Word or LibreOffice; or use the browser's print dialog to save as PDF

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Templates | Jinja2 |
| Interactivity | HTMX (no JavaScript framework required) |
| Styling | PicoCSS |
| Database | SQLite + SQLAlchemy |
| Document generation | python-docx |

No Node.js or build step required.

## Prerequisites

- Python 3.11 or newer

## Installation

```bash
git clone https://github.com/BW1606/RACI-VS.git
cd RACI-VS
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

The SQLite database (`raci_vs.db`) is created automatically on first run.

## Usage

### 1. Create Functions

Go to **Functions** in the navigation bar. Click **Add New Function** and fill in:

- **Name** (required) — unique identifier for the function, e.g. *Project Manager*
- **Parent Function** — select a parent to place this function in the company hierarchy
- **Emergency Representative** — which function covers this one in an emergency
- **Description** — what the function does
- **Aim** — the purpose of this function

Functions can be deleted from the list. Deleting a function removes all its role assignments.

### 2. Create Tasks

Go to **Tasks** and click **Add New Task**. Enter a title and description. Optionally, click **+ Add Function** to assign one or more functions with their RACI-VS roles directly in the creation form — the same role rules apply (selecting **R** reveals the subcategory dropdown). Add as many rows as needed; remove unwanted ones with **✕**. All assignments are saved atomically with the task. Tasks can be deleted from the list.

### 3. Assign Roles

Additional roles can be assigned after creation from a function's or task's detail page. Use the **Assign** form to link a function to a task with one of the six roles:

| Role | Name | Meaning |
|---|---|---|
| R | Responsible | Does the work |
| A | Accountable | Owns the outcome |
| C | Consulted | Provides input beforehand |
| I | Informed | Notified of outcomes |
| V | Verificator | Checks the result |
| S | Signator | Formally signs off |

When **R** is selected, a second dropdown appears to choose a subcategory: *Ausführende Tätigkeit*, *Gewährleistung*, *Koordination*, *Veranlassung*, or *Mitwirkung*. The subcategory is required and is not shown in the matrix — it only appears in the function's exported document.

Each function can hold one role per task. Assignments can be removed from both the function and task detail pages.

### 4. View the Matrix

The **Matrix** page (home) shows all tasks as rows and all functions as columns. Each cell displays the assigned role badge, colour-coded by type.

### 5. View the Organisation Chart

Go to **Organisation** in the navigation bar. Functions are displayed as a top-down tree diagram based on their parent-function relationships. Each box links to the function's detail page.

### 6. Interface Between Two Functions

Go to **Interface**, select two functions, and click **Show Interface**. The page displays every task both functions are involved in, with their respective roles side by side.

## Document Preview & Export

Each document page has two buttons: **Vorschau** opens an HTML preview in a new browser tab, and **Download .docx** downloads the same content as a Word file. The preview page has a **Drucken / PDF** button that triggers the browser's print dialog — use "Save as PDF" to export without downloading a `.docx`.

| Page | Document contents |
|---|---|
| Function detail | Structured 9-section **Funktionsbeschreibung**: Organisatorische Einordnung, Ziel der Funktion, Ergebnisverantwortung (A), Durchführungsverantwortung (R) grouped by subcategory heading, Beratungsverantwortung (C), Informationsverantwortung (I), Verifikationsverantwortung (V), Befugnisse (S), Vertretung. Sections with no assignments show an italic "Details ergänzen" placeholder. |
| Task detail | Task title, description, and a table of all assigned functions with their roles and hierarchy |
| Interface page | Interface header and a table of shared tasks with the role of each function |

The `.docx` files are standard Office Open XML and open in Microsoft Word or LibreOffice.

## How it works

### Database

The app stores everything in a single SQLite file (`raci_vs.db`) managed by SQLAlchemy. There are four tables:

- **`organisations`** — one row per named organisation. All functions and tasks belong to exactly one organisation.
- **`functions`** — one row per organisational function. `organisation_id` scopes each function to its owner. Optional `parent_id` and `emergency_rep_id` are both self-referential foreign keys, enabling arbitrary-depth company hierarchy and emergency coverage chains.
- **`tasks`** — one row per task or activity, scoped by `organisation_id`.
- **`function_task_roles`** — the junction table linking a function to a task. A unique constraint on `(function_id, task_id)` enforces that each function holds at most one role per task. The `role` column stores one of six values (`R`, `A`, `C`, `I`, `V`, `S`). The `r_subcategory` column is only populated when `role = 'R'`; it is `NULL` for all other roles.

### Schema migrations

When a new column is introduced, `main.py` runs migration SQL at startup before `create_all`. Simple column additions use `ALTER TABLE … ADD COLUMN` inside a try/except (skipped silently if the column already exists). More involved migrations — such as removing a unique constraint — rebuild the table in four steps: create a new table with the desired schema, copy data, drop the old table, rename the new one. Fresh installs skip all migrations and let `create_all` build the correct schema from the models directly. The default organisation (`test_org`) is seeded automatically on first run, and any data that pre-dates the multi-organisation feature is assigned to it.

### Request / response cycle

FastAPI handles all HTTP routes. Each request receives a fresh SQLAlchemy session via FastAPI's dependency injection; the session is closed in a `finally` block once the response has been sent. HTML is rendered server-side with Jinja2 templates. HTMX handles partial DOM updates — adding or removing a table row — by swapping a small HTML fragment returned by the server, so the page never fully reloads and no client-side JavaScript framework is needed.

### Role assignment rules

An assignment is rejected with HTTP 400 if the role is not one of the six valid values, if the function-task pair is already assigned, or if role R is submitted without a valid subcategory. For any role other than R the server explicitly sets `r_subcategory` to `NULL` before saving, regardless of what was submitted.

### Document generation

`.docx` files are built entirely in memory by `python-docx`, receiving data directly from the ORM objects. The result is a `BytesIO` buffer that is streamed to the browser as a file download — nothing is written to disk. The function description follows a fixed 9-section structure; any section that has no assigned tasks receives an italic "Details ergänzen" placeholder so the document always matches the expected company template format.

## Project Structure

```
RACI-VS/
├── main.py                   # App entry point, startup migrations, dashboard and interface routes
├── database.py               # SQLAlchemy engine and session
├── models.py                 # ORM models: Organisation, Function, Task, FunctionTaskRole
├── dependencies.py           # Shared FastAPI dependency: get_org_context (active organisation)
├── schemas.py                # Pydantic validation schemas
├── requirements.txt
├── routers/
│   ├── functions.py          # Function CRUD endpoints (org-scoped)
│   ├── tasks.py              # Task CRUD endpoints (org-scoped)
│   ├── assignments.py        # Role assignment endpoints
│   └── documents.py          # .docx download endpoints (org-scoped)
├── services/
│   └── docx_generator.py     # All Word document generation logic
├── static/
│   └── style.css
└── templates/
    ├── base.html             # Shared layout with nav bar and org switcher
    ├── index.html            # Matrix dashboard (tasks × functions)
    ├── functions/            # Function list, detail, and HTMX partials
    ├── tasks/                # Task list, detail, and HTMX partials
    ├── interface/            # Two-function interface view
    ├── organisation/         # Organisation hierarchy chart
    ├── docs/                 # In-browser document preview pages
    └── partials/             # Shared HTMX partial templates
```
