from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import FunctionTaskRole, ROLES, R_SUBCATEGORIES

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
):
    if role not in ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    if role == "R":
        if not r_subcategory or r_subcategory not in R_SUBCATEGORIES:
            raise HTTPException(status_code=400, detail="A subcategory is required for role R")
    else:
        r_subcategory = None
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
        {"request": request, "fr": assignment},
    )


@router.delete("/{assignment_id}", response_class=HTMLResponse)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.get(FunctionTaskRole, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return HTMLResponse("")
