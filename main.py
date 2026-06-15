from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from dependencies import get_org_context
from routers import assignments, documents, functions, tasks
from models import Function, FunctionTaskRole, Organisation, Task

app = FastAPI(title="RACI-VS Manager")

# ── Startup migrations ────────────────────────────────────────────────────────

with engine.connect() as _conn:
    # r_subcategory column (legacy migration)
    try:
        _conn.execute(text("ALTER TABLE function_task_roles ADD COLUMN r_subcategory VARCHAR(50)"))
        _conn.commit()
    except Exception:
        pass  # column already exists

    # Rebuild functions table: drop global unique on name, add organisation_id
    fn_exists = _conn.execute(
        text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='functions'")
    ).fetchone()
    if fn_exists:
        fn_cols = {row[1] for row in _conn.execute(text("PRAGMA table_info(functions)")).fetchall()}
        if "organisation_id" not in fn_cols:
            _conn.execute(text("""
                CREATE TABLE functions_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    parent_id INTEGER,
                    description TEXT DEFAULT '',
                    aim TEXT DEFAULT '',
                    emergency_rep_id INTEGER,
                    created_at DATETIME,
                    organisation_id INTEGER
                )
            """))
            _conn.execute(text(
                "INSERT INTO functions_new "
                "SELECT id, name, parent_id, description, aim, emergency_rep_id, created_at, NULL "
                "FROM functions"
            ))
            _conn.execute(text("DROP TABLE functions"))
            _conn.execute(text("ALTER TABLE functions_new RENAME TO functions"))
            _conn.commit()

    # Rebuild tasks table: drop global unique on title, add organisation_id
    task_exists = _conn.execute(
        text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='tasks'")
    ).fetchone()
    if task_exists:
        task_cols = {row[1] for row in _conn.execute(text("PRAGMA table_info(tasks)")).fetchall()}
        if "organisation_id" not in task_cols:
            _conn.execute(text("""
                CREATE TABLE tasks_new (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(300) NOT NULL,
                    description TEXT DEFAULT '',
                    created_at DATETIME,
                    organisation_id INTEGER
                )
            """))
            _conn.execute(text(
                "INSERT INTO tasks_new SELECT id, title, description, created_at, NULL FROM tasks"
            ))
            _conn.execute(text("DROP TABLE tasks"))
            _conn.execute(text("ALTER TABLE tasks_new RENAME TO tasks"))
            _conn.commit()

Base.metadata.create_all(bind=engine)

# Seed default org and backfill existing rows
with engine.connect() as _conn:
    org_count = _conn.execute(text("SELECT COUNT(*) FROM organisations")).scalar()
    if org_count == 0:
        _conn.execute(text(
            "INSERT INTO organisations (name, created_at) VALUES ('test_org', datetime('now'))"
        ))
        _conn.commit()
    _conn.execute(text(
        "UPDATE functions SET organisation_id = (SELECT id FROM organisations LIMIT 1) "
        "WHERE organisation_id IS NULL"
    ))
    _conn.execute(text(
        "UPDATE tasks SET organisation_id = (SELECT id FROM organisations LIMIT 1) "
        "WHERE organisation_id IS NULL"
    ))
    _conn.commit()

# ── App setup ─────────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(functions.router)
app.include_router(tasks.router)
app.include_router(assignments.router)
app.include_router(documents.router)

templates = Jinja2Templates(directory="templates")

# ── Organisation management ───────────────────────────────────────────────────

@app.post("/organisations")
def create_organisation(name: str = Form(...), db: Session = Depends(get_db)):
    org = Organisation(name=name.strip())
    db.add(org)
    db.commit()
    db.refresh(org)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("current_org_id", str(org.id))
    return resp


@app.get("/organisations/switch/{org_id}")
def switch_organisation(org_id: int, db: Session = Depends(get_db)):
    org = db.get(Organisation, org_id)
    resp = RedirectResponse("/", status_code=303)
    if org:
        resp.set_cookie("current_org_id", str(org_id))
    return resp


# ── Main views ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    all_tasks = db.query(Task).filter(Task.organisation_id == current_org_id).order_by(Task.title).all()
    fn_ids = [f.id for f in all_functions]
    all_roles = (
        db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id.in_(fn_ids)).all()
        if fn_ids else []
    )
    matrix = {(r.function_id, r.task_id): r.role for r in all_roles}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            **org_ctx,
            "functions": all_functions,
            "tasks": all_tasks,
            "matrix": matrix,
        },
    )


@app.get("/organisation", response_class=HTMLResponse)
def organisation(request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    all_fns = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    roots = [f for f in all_fns if f.parent_id is None]
    return templates.TemplateResponse(
        "organisation/index.html",
        {"request": request, **org_ctx, "roots": roots, "title": "Organisation"},
    )


@app.get("/interface", response_class=HTMLResponse)
def interface_select(request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    return templates.TemplateResponse(
        "interface/select.html",
        {
            "request": request,
            **org_ctx,
            "functions": all_functions,
            "f1": None,
            "f2": None,
            "f1_name": None,
            "f2_name": None,
            "shared_tasks": [],
        },
    )


@app.get("/interface/result", response_class=HTMLResponse)
def interface_result(
    request: Request,
    f1: int,
    f2: int,
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    fn1 = db.get(Function, f1)
    fn2 = db.get(Function, f2)
    if fn1 and fn1.organisation_id != current_org_id:
        fn1 = None
    if fn2 and fn2.organisation_id != current_org_id:
        fn2 = None

    shared_tasks = []
    if fn1 and fn2 and f1 != f2:
        roles1 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f1).all()}
        roles2 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f2).all()}
        shared_task_ids = set(roles1.keys()) & set(roles2.keys())
        for tid in shared_task_ids:
            task = db.get(Task, tid)
            shared_tasks.append(
                {
                    "task_id": tid,
                    "task_title": task.title,
                    "task_description": task.description,
                    "role_f1": roles1[tid].role,
                    "role_f2": roles2[tid].role,
                }
            )
        shared_tasks.sort(key=lambda x: x["task_title"])

    return templates.TemplateResponse(
        "interface/select.html",
        {
            "request": request,
            **org_ctx,
            "functions": all_functions,
            "f1": f1,
            "f2": f2,
            "f1_name": fn1.name if fn1 else "",
            "f2_name": fn2.name if fn2 else "",
            "shared_tasks": shared_tasks,
        },
    )
