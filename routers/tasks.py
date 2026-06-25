from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_org_context
from models import Function, FunctionTaskRole, Task, ROLES, R_SUBCATEGORIES, validate_role
from utils import resource_path

router = APIRouter(prefix="/tasks", tags=["tasks"])
templates = Jinja2Templates(directory=resource_path("templates"))


@router.get("", response_class=HTMLResponse)
def list_tasks(request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    tasks = db.query(Task).filter(Task.organisation_id == current_org_id).order_by(Task.title).all()
    functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    return templates.TemplateResponse(
        "tasks/list.html",
        {
            "request": request,
            **org_ctx,
            "tasks": tasks,
            "functions": functions,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.post("", response_class=HTMLResponse)
def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    function_ids: list[int] = Form(default=[]),
    roles: list[str] = Form(default=[]),
    r_subcategories: list[str] = Form(default=[]),
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    if db.query(Task).filter(Task.title == title, Task.organisation_id == current_org_id).first():
        raise HTTPException(status_code=400, detail="Task title already exists")
    task = Task(title=title, description=description, organisation_id=current_org_id)
    db.add(task)
    db.flush()
    padded_subcats = list(r_subcategories) + [""] * max(0, len(function_ids) - len(r_subcategories))
    for fn_id, role, r_sub in zip(function_ids, roles, padded_subcats):
        r_sub = validate_role(role, r_sub or None)
        db.add(FunctionTaskRole(function_id=fn_id, task_id=task.id, role=role, r_subcategory=r_sub))
    db.commit()
    db.refresh(task)
    return templates.TemplateResponse(
        "tasks/_row.html",
        {"request": request, **org_ctx, "task": task},
    )


@router.get("/{task_id}", response_class=HTMLResponse)
def task_detail(task_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    task = db.get(Task, task_id)
    if not task or task.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    assigned_fn_ids = {fr.function_id for fr in task.function_roles}
    available_functions = [f for f in all_functions if f.id not in assigned_fn_ids]
    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            **org_ctx,
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
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    task = db.get(Task, task_id)
    if not task or task.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = title
    task.description = description
    db.commit()
    db.refresh(task)
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    assigned_fn_ids = {fr.function_id for fr in task.function_roles}
    available_functions = [f for f in all_functions if f.id not in assigned_fn_ids]
    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            **org_ctx,
            "task": task,
            "all_functions": all_functions,
            "available_functions": available_functions,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.delete("/{task_id}", response_class=HTMLResponse)
def delete_task(task_id: int, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    task = db.get(Task, task_id)
    if not task or task.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return HTMLResponse("")
