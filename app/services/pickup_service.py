from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Order, PickupSession


def verify_pickup(db: Session, order_id: int, buyer_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    if order.buyer_id != buyer_id:
        return None

    pickup = db.query(PickupSession).filter(PickupSession.order_id == order_id).first()
    if not pickup:
        pickup = PickupSession(
            order_id=order_id,
            buyer_id=buyer_id,
            seller_id=order.seller_id,
            pickup_time=datetime.utcnow(),
            verification_code=f"PK-{order_id}-{buyer_id}",
            status="verified",
        )
        db.add(pickup)
    else:
        pickup.status = "verified"
        pickup.pickup_time = datetime.utcnow()

    order.status = "picked_up"
    db.commit()
    db.refresh(pickup)
    return pickup
