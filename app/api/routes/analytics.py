from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.analytics_service import platform_overview, seller_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return platform_overview(db)


@router.get("/sellers/{seller_id}")
def get_seller_summary(seller_id: int, db: Session = Depends(get_db)):
    return seller_summary(db, seller_id)
