from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.events import emit_event
from app.db.models import ExceptionCase, FulfillmentBatch, Order, SellerProfile


def create_batch(db: Session, seller_id: int):
    seller = db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()
    if not seller:
        return None

    active_batches = db.query(FulfillmentBatch).filter(
        FulfillmentBatch.seller_id == seller_id,
        FulfillmentBatch.status.in_(["batch_created", "preparation_in_progress", "ready_for_pickup", "pickup_window_open"]),
    ).count()

    if active_batches >= 2:
        raise ValueError("Seller already has too many active batches")

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

    emit_event(
        event_name="batch.created",
        entity_type="batch",
        entity_id=batch.id,
        actor_role="seller",
        metadata={"seller_id": seller_id},
    )
    return batch


def seller_queue_snapshot(db: Session, seller_id: int):
    orders = db.query(Order).filter(Order.seller_id == seller_id).order_by(Order.created_at.asc()).all()
    return {
        "seller_id": seller_id,
        "total_orders": len(orders),
        "capacity": {
            "pending": sum(1 for order in orders if order.status in ["created", "validated", "accepted", "preparing", "ready_for_pickup"]),
            "ready": sum(1 for order in orders if order.status == "ready_for_pickup"),
            "picked_up": sum(1 for order in orders if order.status == "picked_up"),
            "failed": sum(1 for order in orders if order.status == "failed"),
        },
        "orders": [{
            "id": order.id,
            "buyer_id": order.buyer_id,
            "status": order.status,
            "requested_slot": order.requested_slot,
            "subtotal": order.subtotal,
        } for order in orders],
    }


def seller_exception_summary(db: Session, seller_id: int):
    orders = db.query(Order).filter(Order.seller_id == seller_id).all()
    order_ids = [order.id for order in orders]
    exceptions = db.query(ExceptionCase).filter(ExceptionCase.order_id.in_(order_ids)).all()
    return {
        "seller_id": seller_id,
        "exception_count": len(exceptions),
        "exceptions": [{
            "id": exc.id,
            "order_id": exc.order_id,
            "type": exc.type,
            "severity": exc.severity,
            "status": exc.status,
        } for exc in exceptions],
    }
