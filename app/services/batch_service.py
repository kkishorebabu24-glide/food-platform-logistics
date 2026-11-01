from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import FulfillmentBatch, SellerProfile


def create_batch(db: Session, seller_id: int):
    seller = db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()
    if not seller:
        return None

    batch = FulfillmentBatch(
        seller_id=seller_id,
        status="batch_created",
        prep_window_start="07:00",
        prep_window_end="07:30",
        ready_time="07:30",
        pickup_window_start="07:30",
        pickup_window_end="08:00",
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch
