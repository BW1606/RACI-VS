from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Function, FunctionTaskRole, Task
from services.docx_generator import (
    generate_function_description,
    generate_interface_description,
    generate_task_description,
)

router = APIRouter(prefix="/docs", tags=["documents"])

_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _docx_response(buf, filename: str) -> StreamingResponse:
    return StreamingResponse(
        buf,
        media_type=_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/function/{fn_id}")
def doc_function(fn_id: int, db: Session = Depends(get_db)):
    fn = db.get(Function, fn_id)
    if not fn:
        raise HTTPException(status_code=404, detail="Function not found")
    buf = generate_function_description(fn)
    safe_name = fn.name.replace(" ", "_")
    return _docx_response(buf, f"Function_{safe_name}.docx")


@router.get("/task/{task_id}")
def doc_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    buf = generate_task_description(task)
    safe_name = task.title.replace(" ", "_")
    return _docx_response(buf, f"Task_{safe_name}.docx")


@router.get("/interface/{f1_id}/{f2_id}")
def doc_interface(f1_id: int, f2_id: int, db: Session = Depends(get_db)):
    fn1 = db.get(Function, f1_id)
    fn2 = db.get(Function, f2_id)
    if not fn1 or not fn2:
        raise HTTPException(status_code=404, detail="Function not found")

    roles1 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f1_id).all()}
    roles2 = {r.task_id: r for r in db.query(FunctionTaskRole).filter(FunctionTaskRole.function_id == f2_id).all()}
    shared_task_ids = set(roles1.keys()) & set(roles2.keys())

    shared_tasks = []
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

    buf = generate_interface_description(fn1, fn2, shared_tasks)
    return _docx_response(buf, f"Interface_{fn1.name}_{fn2.name}.docx".replace(" ", "_"))
