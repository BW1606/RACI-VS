from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Function, FunctionTaskRole, Task, ROLES, R_SUBCATEGORIES

router = APIRouter(prefix="/tasks", tags=["tasks"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def list_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.title).all()
    return templates.TemplateResponse(
        "tasks/list.html",
        {"request": request, "tasks": tasks},
    )


@router.post("", response_class=HTMLResponse)
def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    if db.query(Task).filter(Task.title == title).first():
        raise HTTPException(status_code=400, detail="Task title already exists")
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return templates.TemplateResponse(
        "tasks/_row.html",
        {"request": request, "task": task},
    )


@router.get("/{task_id}", response_class=HTMLResponse)
def task_detail(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    all_functions = db.query(Function).order_by(Function.name).all()
    assigned_fn_ids = {fr.function_id for fr in task.function_roles}
    available_functions = [f for f in all_functions if f.id not in assigned_fn_ids]
    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            "task": task,
            "all_functions": all_functions,
            "available_functions": available_functions,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.post("/{task_id}/edit", response_class=HTMLResponse)
def edit_task(
    task_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = title
    task.description = description
    db.commit()
    db.refresh(task)
    all_functions = db.query(Function).order_by(Function.name).all()
    assigned_fn_ids = {fr.function_id for fr in task.function_roles}
    available_functions = [f for f in all_functions if f.id not in assigned_fn_ids]
    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            "task": task,
            "all_functions": all_functions,
            "available_functions": available_functions,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.delete("/{task_id}", response_class=HTMLResponse)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return HTMLResponse("")
