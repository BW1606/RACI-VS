from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_org_context
from models import Function, FunctionTaskRole, Task, ROLES, R_SUBCATEGORIES, hierarchy_path, validate_role

router = APIRouter(prefix="/functions", tags=["functions"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def list_functions(request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    return templates.TemplateResponse(
        "functions/list.html",
        {
            "request": request,
            **org_ctx,
            "functions": functions,
            "all_functions": functions,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.post("", response_class=HTMLResponse)
def create_function(
    request: Request,
    name: str = Form(...),
    parent_id: str | None = Form(None),
    description: str = Form(""),
    purpose: str = Form(""),
    befugnisse: str = Form(""),
    emergency_rep_id: str | None = Form(None),
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    if db.query(Function).filter(Function.name == name, Function.organisation_id == current_org_id).first():
        raise HTTPException(status_code=400, detail="Function name already exists")
    fn = Function(
        name=name,
        organisation_id=current_org_id,
        parent_id=int(parent_id) if parent_id else None,
        description=description,
        purpose=purpose,
        befugnisse=befugnisse,
        emergency_rep_id=int(emergency_rep_id) if emergency_rep_id else None,
    )
    db.add(fn)
    db.commit()
    db.refresh(fn)
    fn.parent  # eagerly load
    fn.emergency_rep
    return templates.TemplateResponse(
        "functions/_row.html",
        {"request": request, **org_ctx, "fn": fn, "hierarchy_path": hierarchy_path(fn)},
    )


@router.get("/{fn_id}", response_class=HTMLResponse)
def function_detail(fn_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    all_tasks = db.query(Task).filter(Task.organisation_id == current_org_id).order_by(Task.title).all()
    assigned_task_ids = {tr.task_id for tr in fn.task_roles}
    available_tasks = [t for t in all_tasks if t.id not in assigned_task_ids]
    return templates.TemplateResponse(
        "functions/detail.html",
        {
            "request": request,
            **org_ctx,
            "fn": fn,
            "hierarchy_path": hierarchy_path(fn),
            "all_functions": all_functions,
            "available_tasks": available_tasks,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.post("/{fn_id}/assign", response_class=HTMLResponse)
def assign_function_to_task(
    fn_id: int,
    request: Request,
    task_id: int = Form(...),
    role: str = Form(...),
    r_subcategory: str | None = Form(None),
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    r_subcategory = validate_role(role, r_subcategory)
    existing = (
        db.query(FunctionTaskRole)
        .filter(FunctionTaskRole.function_id == fn_id, FunctionTaskRole.task_id == task_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    assignment = FunctionTaskRole(function_id=fn_id, task_id=task_id, role=role, r_subcategory=r_subcategory)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    assignment.task  # eagerly load
    return templates.TemplateResponse(
        "partials/_fn_assignment_row.html",
        {"request": request, **org_ctx, "fr": assignment},
    )


@router.post("/{fn_id}/edit", response_class=HTMLResponse)
def edit_function(
    fn_id: int,
    request: Request,
    name: str = Form(...),
    parent_id: str | None = Form(None),
    description: str = Form(""),
    purpose: str = Form(""),
    befugnisse: str = Form(""),
    emergency_rep_id: str | None = Form(None),
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    fn.name = name
    fn.parent_id = int(parent_id) if parent_id else None
    fn.description = description
    fn.purpose = purpose
    fn.befugnisse = befugnisse
    fn.emergency_rep_id = int(emergency_rep_id) if emergency_rep_id else None
    db.commit()
    db.refresh(fn)
    all_functions = db.query(Function).filter(Function.organisation_id == current_org_id).order_by(Function.name).all()
    all_tasks = db.query(Task).filter(Task.organisation_id == current_org_id).order_by(Task.title).all()
    assigned_task_ids = {tr.task_id for tr in fn.task_roles}
    available_tasks = [t for t in all_tasks if t.id not in assigned_task_ids]
    return templates.TemplateResponse(
        "functions/detail.html",
        {
            "request": request,
            **org_ctx,
            "fn": fn,
            "hierarchy_path": hierarchy_path(fn),
            "all_functions": all_functions,
            "available_tasks": available_tasks,
            "roles": ROLES,
            "r_subcategories": R_SUBCATEGORIES,
        },
    )


@router.delete("/{fn_id}", response_class=HTMLResponse)
def delete_function(fn_id: int, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    current_org_id = org_ctx["current_org_id"]
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    db.delete(fn)
    db.commit()
    return HTMLResponse("")
