from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from routers import assignments, documents, functions, tasks
from models import Function, FunctionTaskRole, Task

app = FastAPI(title="RACI-VS Manager")

with engine.connect() as _conn:
    try:
        _conn.execute(text("ALTER TABLE function_task_roles ADD COLUMN r_subcategory VARCHAR(50)"))
        _conn.commit()
    except Exception:
        pass  # column already exists

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(functions.router)
app.include_router(tasks.router)
app.include_router(assignments.router)
app.include_router(documents.router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    all_functions = db.query(Function).order_by(Function.name).all()
    all_tasks = db.query(Task).order_by(Task.title).all()
    all_roles = db.query(FunctionTaskRole).all()
    matrix = {(r.function_id, r.task_id): r.role for r in all_roles}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "functions": all_functions,
            "tasks": all_tasks,
            "matrix": matrix,
        },
    )


@app.get("/interface", response_class=HTMLResponse)
def interface_select(request: Request, db: Session = Depends(get_db)):
    all_functions = db.query(Function).order_by(Function.name).all()
    return templates.TemplateResponse(
        "interface/select.html",
        {"request": request, "functions": all_functions, "f1": None, "f2": None, "f1_name": None, "f2_name": None, "shared_tasks": []},
    )


@app.get("/interface/result", response_class=HTMLResponse)
def interface_result(request: Request, f1: int, f2: int, db: Session = Depends(get_db)):
    all_functions = db.query(Function).order_by(Function.name).all()
    fn1 = db.get(Function, f1)
    fn2 = db.get(Function, f2)

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
            "functions": all_functions,
            "f1": f1,
            "f2": f2,
            "f1_name": fn1.name if fn1 else "",
            "f2_name": fn2.name if fn2 else "",
            "shared_tasks": shared_tasks,
        },
    )
