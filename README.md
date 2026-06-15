# RACI-VS Matrix Manager

A locally-running web app for managing RACI-VS responsibility matrices across company functions and tasks, with Word document export.

## Features

- **Function management** — create functions with company hierarchy, description, aim, and emergency representative
- **Task management** — create tasks with descriptions and assign functions to them with RACI-VS roles
- **Matrix view** — live overview table of all functions vs. tasks with colour-coded roles
- **Interface analysis** — select any two functions to see the tasks they share and their respective roles
- **Word document export** — generate `.docx` reports for function descriptions, task descriptions, and function interfaces

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Templates | Jinja2 |
| Interactivity | HTMX (no JavaScript required) |
| Styling | PicoCSS |
| Database | SQLite + SQLAlchemy |
| Document generation | python-docx |

No Node.js or build step required.

## Prerequisites

- Python 3.11 or newer

## Installation

```bash
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

Go to **Tasks** and click **Add New Task**. Enter a title and description. Tasks can be deleted from the list.

### 3. Assign Roles

Open a task's detail page. Use the **Assign** form at the bottom to link a function to this task with one of the six roles:

| Role | Name | Meaning |
|---|---|---|
| R | Responsible | Does the work |
| A | Accountable | Owns the outcome |
| C | Consulted | Provides input beforehand |
| I | Informed | Notified of outcomes |
| V | Verificator | Checks the result |
| S | Signator | Formally signs off |

Each function can hold one role per task. Assignments can be removed from the task detail page.

### 4. View the Matrix

The **Matrix** page (home) shows all functions as rows and all tasks as columns. Each cell displays the assigned role badge, colour-coded by type.

### 5. Interface Between Two Functions

Go to **Interface**, select two functions, and click **Show Interface**. The page displays every task both functions are involved in, with their respective roles side by side.

## Document Export

All documents are standard `.docx` files that open in Microsoft Word or LibreOffice.

| Button / Link | Document contents |
|---|---|
| *Download .docx* on a Function page | Function name, hierarchy path, description, aim, emergency rep, and a table of all tasks with roles |
| *Download .docx* on a Task page | Task title, description, and a table of all assigned functions with their roles and hierarchy |
| *Download .docx* on the Interface page | Interface header, and a table of shared tasks with the role of each function in every shared task |

## Project Structure

```
RACI-VS/
├── main.py                   # App entry point, dashboard and interface routes
├── database.py               # SQLAlchemy engine and session
├── models.py                 # ORM models: Function, Task, FunctionTaskRole
├── schemas.py                # Pydantic validation schemas
├── requirements.txt
├── routers/
│   ├── functions.py          # Function CRUD endpoints
│   ├── tasks.py              # Task CRUD endpoints
│   ├── assignments.py        # Role assignment endpoints
│   └── documents.py          # .docx download endpoints
├── services/
│   └── docx_generator.py     # All Word document generation logic
├── static/
│   └── style.css
└── templates/
    ├── base.html             # Shared layout with nav bar
    ├── index.html            # Matrix dashboard
    ├── functions/            # Function list, detail, and HTMX partials
    ├── tasks/                # Task list, detail, and HTMX partials
    ├── interface/            # Two-function interface view
    └── partials/             # Shared HTMX partial templates
```
