from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.events import emit_event
from app.core.state_machine import assert_valid_transition
from app.db.models import ExceptionCase, Order, OrderItem, OrderStatusHistory, SellerCapacity, SellerProfile, User
from app.schemas.order import OrderCreate


def create_order(db: Session, payload: OrderCreate):
    seller = db.query(SellerProfile).filter(SellerProfile.id == payload.seller_id).first()
    if not seller:
        raise ValueError("Seller not found")

    buyer = db.query(User).filter(User.id == payload.buyer_id).first()
    if not buyer:
        raise ValueError("Buyer not found")

    capacity = db.query(SellerCapacity).filter(SellerCapacity.seller_id == payload.seller_id).first()
    if capacity is None:
        capacity = SellerCapacity(
            seller_id=payload.seller_id,
            slot_start="00:00",
            slot_end="23:59",
            max_orders=20,
            active_order_count=0,
            status="open",
        )
        db.add(capacity)
        db.flush()

    active_orders = db.query(Order).filter(
        Order.seller_id == payload.seller_id,
        Order.status.notin_(["cancelled", "refunded", "completed", "failed"]),
    ).count()

    if active_orders >= capacity.max_orders:
        raise ValueError("Seller capacity exceeded for this slot")

    subtotal = sum(item.unit_price * item.quantity for item in payload.items)
    order = Order(
        buyer_id=payload.buyer_id,
        seller_id=payload.seller_id,
        status="created",
        requested_slot=payload.requested_slot,
        subtotal=subtotal,
        payment_status="pending",
    )
    db.add(order)
    db.flush()

    for item in payload.items:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        db.add(order_item)

    db.add(
        OrderStatusHistory(
            order_id=order.id,
            old_status=None,
            new_status="created",
            changed_by="system",
            reason="initial_order_creation",
        )
    )

    db.commit()
    db.refresh(order)

    emit_event(
        event_name="order.created",
        entity_type="order",
        entity_id=order.id,
        actor_id=payload.buyer_id,
        actor_role="buyer",
        metadata={"seller_id": payload.seller_id, "subtotal": subtotal},
    )
    return order


def maybe_log_exception(db: Session, order_id: int, status: str, reason: Optional[str] = None):
    if status not in {"delayed", "failed"}:
        return None
    exception = ExceptionCase(
        order_id=order_id,
        batch_id=None,
        type=status,
        severity="high" if status == "failed" else "medium",
        status="open",
        raised_by="system",
    )
    db.add(exception)
    emit_event(
        event_name=f"exception.{status}",
        entity_type="order",
        entity_id=order_id,
        actor_role="system",
        metadata={"reason": reason or status},
    )
    return exception


def list_orders(db: Session):
    return db.query(Order).order_by(Order.created_at.desc()).all()


def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, status: str, reason: str | None = None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    current_status = order.status
    assert_valid_transition(current_status, status)

    previous_status = order.status
    order.status = status
    order.updated_at = datetime.utcnow()

    db.add(
        OrderStatusHistory(
            order_id=order.id,
            old_status=previous_status,
            new_status=status,
            changed_by="system",
            reason=reason or "status_updated",
        )
    )

    if status in {"delayed", "failed"}:
        maybe_log_exception(db, order.id, status, reason)

    db.commit()
    db.refresh(order)

    emit_event(
        event_name=f"order.{status}",
        entity_type="order",
        entity_id=order.id,
        actor_role="system",
        metadata={"from_status": previous_status, "reason": reason},
    )
    return order
