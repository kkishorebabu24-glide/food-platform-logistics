from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.services.analytics_service import dashboard_summary, platform_overview, seller_summary
from app.services.batch_service import seller_exception_summary, seller_queue_snapshot

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AdminActionRequest(BaseModel):
    action: str
    reason: str
    seller_id: int | None = None
    order_id: int | None = None


@router.get("/overview")
def get_overview(db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "seller"))):
    return platform_overview(db)


@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "seller"))):
    return dashboard_summary(db)


@router.get("/sellers/{seller_id}")
def get_seller_summary(seller_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "seller"))):
    return seller_summary(db, seller_id)


@router.get("/queue/{seller_id}")
def get_queue_summary(seller_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "seller"))):
    return seller_queue_snapshot(db, seller_id)


@router.get("/exceptions/{seller_id}")
def get_exception_summary(seller_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "seller"))):
    return seller_exception_summary(db, seller_id)


@router.post("/admin-action")
def record_admin_action(payload: AdminActionRequest, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("admin"))):
    if not payload.action:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action is required")

    return {
        "ok": True,
        "actor": current_user,
        "action": payload.action,
        "reason": payload.reason,
        "seller_id": payload.seller_id,
        "order_id": payload.order_id,
        "message": "Admin action recorded",
    }
