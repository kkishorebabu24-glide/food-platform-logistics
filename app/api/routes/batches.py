from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.batch_service import create_batch

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_batch_route(seller_id: int, db: Session = Depends(get_db)):
    batch = create_batch(db, seller_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    return batch
