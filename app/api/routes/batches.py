from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.db.database import get_db
from app.services.batch_service import create_batch

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", status_code=201)
def create_batch_route(
    seller_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("seller", "admin")),
):
    try:
        batch = create_batch(db, seller_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not batch:
        raise HTTPException(status_code=404, detail="Seller not found")
    return batch
