from fastapi import Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models import DEFAULT_ORG_NAME, Organisation


def get_org_context(request: Request, db: Session = Depends(get_db)) -> dict:
    all_orgs = db.query(Organisation).order_by(Organisation.name).all()
    if not all_orgs:
        default = Organisation(name=DEFAULT_ORG_NAME)
        db.add(default)
        db.commit()
        db.refresh(default)
        all_orgs = [default]
    cookie_val = request.cookies.get("current_org_id")
    try:
        current_org_id = int(cookie_val) if cookie_val is not None else all_orgs[0].id
    except (ValueError, TypeError):
        current_org_id = all_orgs[0].id
    current_org = next((o for o in all_orgs if o.id == current_org_id), all_orgs[0])
    return {"all_orgs": all_orgs, "current_org": current_org, "current_org_id": current_org.id}
