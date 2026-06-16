from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_org_context
from models import Function, FunctionTaskRole, validate_role

router = APIRouter(prefix="/assignments", tags=["assignments"])
templates = Jinja2Templates(directory="templates")


@router.post("", response_class=HTMLResponse)
def create_assignment(
    request: Request,
    function_id: int = Form(...),
    task_id: int = Form(...),
    role: str = Form(...),
    r_subcategory: str | None = Form(None),
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    fn = db.get(Function, function_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    r_subcategory = validate_role(role, r_subcategory)
    existing = (
        db.query(FunctionTaskRole)
        .filter(FunctionTaskRole.function_id == function_id, FunctionTaskRole.task_id == task_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    assignment = FunctionTaskRole(function_id=function_id, task_id=task_id, role=role, r_subcategory=r_subcategory)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return templates.TemplateResponse(
        "partials/_assignment_row.html",
        {"request": request, "fr": assignment, **org_ctx},
    )


@router.delete("/{assignment_id}", response_class=HTMLResponse)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    assignment = db.get(FunctionTaskRole, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    fn = db.get(Function, assignment.function_id)
    if not fn or fn.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return HTMLResponse("")
