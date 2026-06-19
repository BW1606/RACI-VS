import io
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_org_context
from models import Function, FunctionTaskRole, Organisation, Task, validate_role

router = APIRouter(prefix="/organisations", tags=["organisations"])


def _unique_org_name(base_name: str, db: Session) -> str:
    existing = {o.name for o in db.query(Organisation).all()}
    if base_name not in existing:
        return base_name
    counter = 2
    while f"{base_name} ({counter})" in existing:
        counter += 1
    return f"{base_name} ({counter})"


def _validate_payload(data: dict) -> None:
    required = {"version", "organisation", "functions", "tasks", "assignments"}
    missing = required - data.keys()
    if missing:
        raise HTTPException(status_code=400, detail=f"Invalid export file: missing keys {missing}")
    if "name" not in data["organisation"]:
        raise HTTPException(status_code=400, detail="Missing organisation.name")


@router.get("/export")
def export_organisation(
    db: Session = Depends(get_db),
    org_ctx: dict = Depends(get_org_context),
):
    current_org_id = org_ctx["current_org_id"]
    org = db.get(Organisation, current_org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    functions = (
        db.query(Function)
        .filter(Function.organisation_id == current_org_id)
        .all()
    )
    tasks = (
        db.query(Task)
        .filter(Task.organisation_id == current_org_id)
        .all()
    )
    fn_ids = [f.id for f in functions]
    assignments = (
        db.query(FunctionTaskRole)
        .filter(FunctionTaskRole.function_id.in_(fn_ids))
        .all()
        if fn_ids else []
    )

    fn_ref = {f.id: f"f{f.id}" for f in functions}
    task_ref = {t.id: f"t{t.id}" for t in tasks}

    payload = {
        "version": "1.0",
        "organisation": {"name": org.name},
        "functions": [
            {
                "ref": fn_ref[f.id],
                "name": f.name,
                "description": f.description or "",
                "purpose": f.purpose or "",
                "parent_ref": fn_ref.get(f.parent_id) if f.parent_id else None,
                "emergency_rep_ref": fn_ref.get(f.emergency_rep_id) if f.emergency_rep_id else None,
            }
            for f in functions
        ],
        "tasks": [
            {
                "ref": task_ref[t.id],
                "title": t.title,
                "description": t.description or "",
            }
            for t in tasks
        ],
        "assignments": [
            {
                "function_ref": fn_ref[a.function_id],
                "task_ref": task_ref[a.task_id],
                "role": a.role,
                "r_subcategory": a.r_subcategory,
            }
            for a in assignments
        ],
    }

    json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    safe_name = org.name.replace(" ", "_").replace("/", "-")
    filename = f"{safe_name}_export.json"

    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import")
async def import_organisation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not (file.filename or "").endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    _validate_payload(data)

    try:
        base_name = data["organisation"]["name"].strip()
        org_name = _unique_org_name(base_name, db)
        new_org = Organisation(name=org_name)
        db.add(new_org)
        db.flush()

        # First pass: create functions without hierarchy links
        ref_to_fn_id: dict[str, int] = {}
        for fn_data in data["functions"]:
            ref = fn_data.get("ref")
            name = (fn_data.get("name") or "").strip()
            if not ref or not name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Function entry missing 'ref' or 'name': {fn_data}",
                )
            fn = Function(
                name=name,
                organisation_id=new_org.id,
                description=fn_data.get("description", ""),
                purpose=fn_data.get("purpose", fn_data.get("aim", "")),
                parent_id=None,
                emergency_rep_id=None,
            )
            db.add(fn)
            db.flush()
            ref_to_fn_id[ref] = fn.id

        # Second pass: resolve parent and emergency_rep references
        for fn_data in data["functions"]:
            ref = fn_data["ref"]
            fn = db.get(Function, ref_to_fn_id[ref])

            parent_ref = fn_data.get("parent_ref")
            if parent_ref:
                if parent_ref not in ref_to_fn_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unknown parent_ref '{parent_ref}' for function '{fn_data.get('name')}'",
                    )
                fn.parent_id = ref_to_fn_id[parent_ref]

            emergency_ref = fn_data.get("emergency_rep_ref")
            if emergency_ref:
                if emergency_ref not in ref_to_fn_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unknown emergency_rep_ref '{emergency_ref}' for function '{fn_data.get('name')}'",
                    )
                fn.emergency_rep_id = ref_to_fn_id[emergency_ref]

        # Create tasks
        ref_to_task_id: dict[str, int] = {}
        for task_data in data["tasks"]:
            ref = task_data.get("ref")
            title = (task_data.get("title") or "").strip()
            if not ref or not title:
                raise HTTPException(
                    status_code=400,
                    detail=f"Task entry missing 'ref' or 'title': {task_data}",
                )
            task = Task(
                title=title,
                description=task_data.get("description", ""),
                organisation_id=new_org.id,
            )
            db.add(task)
            db.flush()
            ref_to_task_id[ref] = task.id

        # Create assignments
        for asgn in data["assignments"]:
            fn_ref_key = asgn.get("function_ref")
            task_ref_key = asgn.get("task_ref")
            role = asgn.get("role")
            r_subcategory = asgn.get("r_subcategory")

            if fn_ref_key not in ref_to_fn_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown function_ref '{fn_ref_key}' in assignment",
                )
            if task_ref_key not in ref_to_task_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown task_ref '{task_ref_key}' in assignment",
                )

            r_subcategory = validate_role(role, r_subcategory)

            db.add(FunctionTaskRole(
                function_id=ref_to_fn_id[fn_ref_key],
                task_id=ref_to_task_id[task_ref_key],
                role=role,
                r_subcategory=r_subcategory,
            ))

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}") from exc

    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("current_org_id", str(new_org.id))
    return resp
