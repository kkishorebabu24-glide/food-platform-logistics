from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Order, OrderItem, SellerProfile, User
from app.schemas.order import OrderCreate


def create_order(db: Session, payload: OrderCreate):
    seller = db.query(SellerProfile).filter(SellerProfile.id == payload.seller_id).first()
    if not seller:
        raise ValueError("Seller not found")

    buyer = db.query(User).filter(User.id == payload.buyer_id).first()
    if not buyer:
        raise ValueError("Buyer not found")

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

    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session):
    return db.query(Order).order_by(Order.created_at.desc()).all()


def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, status: str, reason: str | None = None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order
