from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.queue_service import seller_queue_snapshot, seller_exception_summary

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/queue/{seller_id}")
def seller_queue(seller_id: int, db: Session = Depends(get_db)):
    return seller_queue_snapshot(db, seller_id)


@router.get("/exceptions/{seller_id}")
def seller_exceptions(seller_id: int, db: Session = Depends(get_db)):
    return seller_exception_summary(db, seller_id)
