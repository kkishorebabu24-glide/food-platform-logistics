from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.db.models import ExceptionCase
from app.core.events import emit_event

router = APIRouter(prefix="/admin", tags=["admin"])


class RaiseExceptionRequest(BaseModel):
    order_id: int | None = None
    batch_id: int | None = None
    exception_type: str = "delay"
    severity: str = "medium"
    reason: str = "manual_review"


@router.post("/exceptions")
def create_exception(
    payload: RaiseExceptionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    exc = ExceptionCase(
        order_id=payload.order_id,
        batch_id=payload.batch_id,
        type=payload.exception_type,
        severity=payload.severity,
        status="open",
        raised_by=current_user["email"],
    )
    db.add(exc)
    db.commit()
    db.refresh(exc)

    emit_event(
        event_name="admin.exception.created",
        entity_type="exception_case",
        entity_id=exc.id,
        actor_id=current_user["user_id"],
        actor_role=current_user["role"],
        metadata={"order_id": payload.order_id, "batch_id": payload.batch_id, "type": payload.exception_type},
    )

    return {"ok": True, "exception_id": exc.id, "status": exc.status}


@router.get("/health")
def admin_health(_: dict = Depends(require_roles("admin", "seller"))):
    return {"ok": True, "message": "admin operations available"}
