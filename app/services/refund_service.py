from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.events import emit_event
from app.db.models import Order, PickupSession


def mark_no_show(db: Session, order_id: int, reason: str = "no_show") -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"ok": False, "detail": "order_not_found"}

    order.status = "failed"
    order.updated_at = datetime.utcnow()

    emit_event(
        event_name="pickup.no_show",
        entity_type="order",
        entity_id=order.id,
        actor_role="system",
        metadata={"reason": reason, "seller_id": order.seller_id, "buyer_id": order.buyer_id},
    )

    db.commit()
    return {"ok": True, "order_id": order.id, "status": order.status, "reason": reason}


def issue_refund(db: Session, order_id: int, reason: str = "pickup_failed") -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"ok": False, "detail": "order_not_found"}

    order.status = "refund_pending"
    order.updated_at = datetime.utcnow()

    emit_event(
        event_name="refund.initiated",
        entity_type="order",
        entity_id=order.id,
        actor_role="admin",
        metadata={"reason": reason, "amount": order.subtotal},
    )

    db.commit()
    return {"ok": True, "order_id": order.id, "status": order.status, "refund_amount": order.subtotal}
