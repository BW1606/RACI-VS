from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_org_context
from models import Function, FunctionTaskRole, Task, hierarchy_path
from services.docx_generator import (
    R_SUBCATEGORY_HEADINGS,
    R_SUBCATEGORY_ORDER,
    generate_function_description,
    generate_interface_description,
    generate_task_description,
)

router = APIRouter(prefix="/docs", tags=["documents"])
templates = Jinja2Templates(directory="templates")

_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def get_shared_tasks(db: Session, f1_id: int, f2_id: int) -> list[dict]:
    roles1 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f1_id).all()}
    roles2 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f2_id).all()}
    shared = []
    for tid in set(roles1) & set(roles2):
        task = db.get(Task, tid)
        shared.append({
            "task_id": tid,
            "task_title": task.title,
            "task_description": task.description,
            "role_f1": roles1[tid].role,
            "role_f2": roles2[tid].role,
        })
    shared.sort(key=lambda x: x["task_title"])
    return shared


def _docx_response(buf, filename: str) -> StreamingResponse:
    return StreamingResponse(
        buf,
        media_type=_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/function/{fn_id}")
def doc_function(fn_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != org_ctx["current_org_id"]:
        raise HTTPException(status_code=404, detail="Function not found")
    buf = generate_function_description(fn)
    safe_name = fn.name.replace(" ", "_")
    return _docx_response(buf, f"Function_{safe_name}.docx")


@router.get("/task/{task_id}")
def doc_task(task_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    task = db.get(Task, task_id)
    if not task or task.organisation_id != org_ctx["current_org_id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    buf = generate_task_description(task)
    safe_name = task.title.replace(" ", "_")
    return _docx_response(buf, f"Task_{safe_name}.docx")


@router.get("/interface/{f1_id}/{f2_id}")
def doc_interface(
    f1_id: int,
    f2_id: int,
    request: Request,
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    fn1 = db.get(Function, f1_id)
    fn2 = db.get(Function, f2_id)
    if not fn1 or fn1.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    if not fn2 or fn2.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")

    shared_tasks = get_shared_tasks(db, f1_id, f2_id)
    buf = generate_interface_description(fn1, fn2, shared_tasks)
    return _docx_response(buf, f"Interface_{fn1.name}_{fn2.name}.docx".replace(" ", "_"))


@router.get("/function/{fn_id}/preview", response_class=HTMLResponse)
def preview_function(fn_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    fn = db.get(Function, fn_id)
    if not fn or fn.organisation_id != org_ctx["current_org_id"]:
        raise HTTPException(status_code=404, detail="Function not found")

    parent_chain = hierarchy_path(fn.parent) or "—"

    children_names = ", ".join(c.name for c in fn.children) if fn.children else "—"

    by_role: dict[str, list] = {"A": [], "R": [], "C": [], "I": [], "V": [], "S": []}
    for tr in fn.task_roles:
        if tr.role in by_role:
            by_role[tr.role].append(tr)

    by_r_sub: dict[str, list] = {s: [] for s in R_SUBCATEGORY_ORDER}
    for tr in by_role["R"]:
        sub = tr.r_subcategory or "Ausführende Tätigkeit"
        if sub in by_r_sub:
            by_r_sub[sub].append(tr)

    return templates.TemplateResponse("docs/function_preview.html", {
        "request": request,
        "fn": fn,
        "parent_chain": parent_chain,
        "children_names": children_names,
        "by_role": by_role,
        "by_r_sub": by_r_sub,
        "r_subcategory_order": R_SUBCATEGORY_ORDER,
        "r_subcategory_headings": R_SUBCATEGORY_HEADINGS,
        **org_ctx,
    })


@router.get("/task/{task_id}/preview", response_class=HTMLResponse)
def preview_task(task_id: int, request: Request, db: Session = Depends(get_db), org_ctx: dict = Depends(get_org_context)):
    task = db.get(Task, task_id)
    if not task or task.organisation_id != org_ctx["current_org_id"]:
        raise HTTPException(status_code=404, detail="Task not found")

    function_rows = [
        {"fr": fr, "hierarchy": hierarchy_path(fr.function)}
        for fr in task.function_roles
    ]

    return templates.TemplateResponse("docs/task_preview.html", {
        "request": request,
        "task": task,
        "function_rows": function_rows,
        **org_ctx,
    })


@router.get("/interface/{f1_id}/{f2_id}/preview", response_class=HTMLResponse)
def preview_interface(
    f1_id: int,
    f2_id: int,
    request: Request,
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    fn1 = db.get(Function, f1_id)
    fn2 = db.get(Function, f2_id)
    if not fn1 or fn1.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")
    if not fn2 or fn2.organisation_id != current_org_id:
        raise HTTPException(status_code=404, detail="Function not found")

    shared_tasks = get_shared_tasks(db, f1_id, f2_id)

    return templates.TemplateResponse("docs/interface_preview.html", {
        "request": request,
        "fn1": fn1,
        "fn2": fn2,
        "shared_tasks": shared_tasks,
        **org_ctx,
    })
