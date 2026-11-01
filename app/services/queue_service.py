from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ExceptionCase, FulfillmentBatch, Order, OrderStatusHistory


def seller_queue_snapshot(db: Session, seller_id: int):
    orders = db.query(Order).filter(Order.seller_id == seller_id).order_by(Order.created_at.asc()).all()
    return {
        "seller_id": seller_id,
        "total_orders": len(orders),
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
