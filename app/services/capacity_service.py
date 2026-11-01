from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.events import emit_event
from app.db.models import Order, SellerCapacity, SellerProfile


def get_or_create_seller_capacity(db: Session, seller_id: int, slot: str | None = None) -> SellerCapacity:
    slot_name = slot or "default"
    capacity = db.query(SellerCapacity).filter(
        SellerCapacity.seller_id == seller_id,
        SellerCapacity.slot_start == slot_name,
    ).first()

    if capacity is None:
        capacity = SellerCapacity(
            seller_id=seller_id,
            slot_start=slot_name,
            slot_end=slot_name,
            max_orders=20,
            active_order_count=0,
            status="open",
        )
        db.add(capacity)
        db.flush()

    return capacity


def check_seller_capacity(db: Session, seller_id: int, slot: str | None = None, threshold: int | None = None) -> dict:
    capacity = get_or_create_seller_capacity(db, seller_id, slot)
    active_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status.notin_(["cancelled", "completed", "refunded", "failed"]),
    ).count()

    limit = threshold or capacity.max_orders
    available = max(limit - active_orders, 0)

    payload = {
        "seller_id": seller_id,
        "slot": slot or capacity.slot_start,
        "capacity_limit": limit,
        "active_orders": active_orders,
        "available_slots": available,
        "status": "open" if available > 0 else "full",
    }

    emit_event(
        event_name="seller.capacity.checked",
        entity_type="seller_capacity",
        entity_id=capacity.id,
        actor_role="system",
        metadata=payload,
    )
    return payload


def seller_queue_thresholds(db: Session, seller_id: int) -> dict:
    seller = db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()
    if not seller:
        return {"seller_id": seller_id, "error": "seller_not_found"}

    active_orders = db.query(Order).filter(Order.seller_id == seller_id).count()
    return {
        "seller_id": seller_id,
        "seller_name": seller.seller_name,
        "active_orders": active_orders,
        "warning_threshold": 12,
        "critical_threshold": 18,
        "queue_health": "healthy" if active_orders < 12 else "warning" if active_orders < 18 else "critical",
        "updated_at": datetime.utcnow().isoformat(),
    }
