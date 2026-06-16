# RACI-VS Matrix Manager

A web app for managing RACI-VS responsibility matrices across company functions and tasks, with Word document export. Supports multiple independent organisations in a single database.

Available as a **Windows desktop app** (no Python or terminal required for end users) and as a standard Python/FastAPI server for developers.

## Features

- **Multi-organisation support** — create any number of named organisations; each has its own isolated set of functions, tasks, and assignments. Switch between them from the nav bar; new organisations start completely empty.
- **Function management** — create functions with company hierarchy, description, aim, and emergency representative
- **Task management** — create tasks with descriptions and assign functions to them with RACI-VS roles
- **R-role subcategory** — Responsible (R) assignments carry one of five subcategories (Ausführende Tätigkeit, Gewährleistung, Koordination, Veranlassung, Mitwirkung); visible in the function document, not in the matrix
- **Matrix view** — live overview table: tasks as rows, functions as columns, with colour-coded role badges
- **Organisation chart** — visual top-down hierarchy diagram of all functions in the active organisation, based on parent-function relationships
- **Interface analysis** — select any two functions to see the tasks they share and their respective roles
- **Document preview & export** — view function descriptions, task descriptions, and interface reports directly in the browser as a formatted HTML page (opens in a new tab); download as `.docx` for Word or LibreOffice; or use the browser's print dialog to save as PDF
- **Organisation export / import** — back up the active organisation or share it with a colleague as a single `.json` file; importing creates a new, fully independent copy (functions with their hierarchy, tasks, and all role assignments are restored; if the name already exists a numeric suffix is added automatically)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Templates | Jinja2 |
| Interactivity | HTMX (no JavaScript framework required) |
| Styling | PicoCSS |
| Database | SQLite + SQLAlchemy |
| Document generation | python-docx |
| Desktop packaging | PyInstaller + pystray + Pillow |

No Node.js required.

## Installation & Running

### End users — Windows desktop app

Download `RACI-VS_Setup.exe` from the [Releases page](https://github.com/BW1606/RACI-VS/releases) and run it. The installer creates a Start Menu entry and an optional Desktop shortcut. No Python or command-line tools needed.

Launch the app from the Desktop shortcut or Start Menu. A tray icon appears in the Windows taskbar notification area and the browser opens automatically to the app. Right-click the tray icon for **Open RACI-VS** and **Quit** options.

The database is stored in `%APPDATA%\RACI-VS\raci_vs.db` and is preserved across app updates.

### Developers — run from source

```bash
git clone https://github.com/BW1606/RACI-VS.git
cd RACI-VS
git checkout feature/desktop-app
pip install -r requirements.txt
```

**Run with the desktop launcher** (system tray + auto-open browser):
```bash
python launcher.py
```

**Run as a development server** (hot-reload, no tray icon):
```bash
uvicorn main:app --reload
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

## Building the Installer

To produce a distributable `RACI-VS_Setup.exe`, you need Python 3.11+, the project dependencies, and [Inno Setup](https://jrsoftware.org/isinfo.php) installed on your build machine.

**Step 1 — bundle the app with PyInstaller:**
```bat
build.bat
```
Output: `dist\RACI-VS\` folder containing `RACI-VS.exe` and all dependencies.

**Step 2 — compile the installer:**
Open [raci_vs.iss](raci_vs.iss) in Inno Setup Compiler and click **Build → Compile**.
Output: `RACI-VS_Setup.exe` — a self-contained Windows installer ready to distribute.

> **SmartScreen warning:** because the `.exe` is not code-signed, Windows may show a *"Windows protected your PC"* prompt on first run. Click **More info → Run anyway** to proceed. This is expected for unsigned software distributed outside the Microsoft Store.

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

## Organisation Export & Import

The active organisation can be exported as a portable `.json` file and imported on any machine running the app.

**To export:** open the org-switcher dropdown in the top-left of the nav bar and click **⬇ Export current org**. The browser downloads `<org-name>_export.json`.

**To import:** click **⬆ Import org (.json)** in the same dropdown and pick a previously exported file. An example organisation (`examples/Beispiel-org.json`) is included in the repository and can be imported directly to explore the app with pre-filled data. The file is uploaded immediately (no separate submit button). A new organisation is created with all the original functions (including parent hierarchy and emergency-representative links), tasks, and role assignments. If an organisation with the same name already exists, a suffix is appended (e.g. *MyOrg (2)*), and the imported org becomes the active one.

The `.json` format is human-readable and version-tagged:

```json
{
  "version": "1.0",
  "organisation": { "name": "MyOrg" },
  "functions": [
    { "ref": "f1", "name": "CEO", "description": "", "aim": "",
      "parent_ref": null, "emergency_rep_ref": null }
  ],
  "tasks": [
    { "ref": "t1", "title": "Budgetplanung", "description": "" }
  ],
  "assignments": [
    { "function_ref": "f1", "task_ref": "t1", "role": "A", "r_subcategory": null }
  ]
}
```

## Document Preview & Export

Each document page has two buttons: **Vorschau** opens an HTML preview in a new browser tab, and **Download .docx** downloads the same content as a Word file. The preview page has a **Drucken / PDF** button that triggers the browser's print dialog — use "Save as PDF" to export without downloading a `.docx`.

| Page | Document contents |
|---|---|
| Function detail | Structured 9-section **Funktionsbeschreibung**: Organisatorische Einordnung, Ziel der Funktion, Ergebnisverantwortung (A), Durchführungsverantwortung (R) grouped by subcategory heading, Beratungsverantwortung (C), Informationsverantwortung (I), Verifikationsverantwortung (V), Befugnisse (S), Vertretung. Sections with no assignments show an italic "Details ergänzen" placeholder. |
| Task detail | Task title, description, and a table of all assigned functions with their roles and hierarchy |
| Interface page | Interface header and a table of shared tasks with the role of each function |

The `.docx` files are standard Office Open XML and open in Microsoft Word or LibreOffice.

## How it works

### Desktop launcher

`launcher.py` is the entry point for the packaged Windows app. It starts the FastAPI server (via `uvicorn`) in a background daemon thread, waits 1.5 seconds for the server to bind, then opens the default browser to `http://127.0.0.1:8000`. A `pystray` system-tray icon keeps the process alive and provides **Open** and **Quit** menu items. Quitting calls `os._exit(0)`, which cleanly terminates the daemon thread along with the main process.

When PyInstaller freezes the app, all source files and the `static/` and `templates/` directories are bundled into a temporary extraction folder (`sys._MEIPASS`). `resource_path()` in `main.py` resolves asset paths against `sys._MEIPASS` when frozen and against `__file__` when running from source, so both modes work without any path changes.

### Database

The app stores everything in a single SQLite file managed by SQLAlchemy. When running as a packaged desktop app the file is stored at `%APPDATA%\RACI-VS\raci_vs.db` (always writable, survives updates). When running from source it sits next to `database.py` as `raci_vs.db`. There are four tables:

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
├── launcher.py               # Desktop entry point: uvicorn thread + browser open + system tray
├── main.py                   # FastAPI app, startup migrations, dashboard and interface routes
├── database.py               # SQLAlchemy engine and session (path-aware for frozen builds)
├── models.py                 # ORM models: Organisation, Function, Task, FunctionTaskRole
├── dependencies.py           # Shared FastAPI dependency: get_org_context (active organisation)
├── schemas.py                # Pydantic validation schemas
├── requirements.txt
├── build.bat                 # PyInstaller build script → dist\RACI-VS\RACI-VS.exe
├── raci_vs.iss               # Inno Setup script → RACI-VS_Setup.exe installer
├── routers/
│   ├── functions.py          # Function CRUD endpoints (org-scoped)
│   ├── tasks.py              # Task CRUD endpoints (org-scoped)
│   ├── assignments.py        # Role assignment endpoints
│   ├── documents.py          # .docx download endpoints (org-scoped)
│   └── organisations.py      # Organisation export and import endpoints
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
