from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.pickup_service import verify_pickup

router = APIRouter(prefix="/pickups", tags=["pickups"])


@router.post("/verify")
def verify_pickup_route(order_id: int, buyer_id: int, db: Session = Depends(get_db)):
    pickup = verify_pickup(db, order_id=order_id, buyer_id=buyer_id)
    if not pickup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup record not found")
    return pickup
