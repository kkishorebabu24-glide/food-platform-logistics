from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from app.core.events import emit_event
from app.db.models import ExceptionCase, Order, SellerProfile


def seller_summary(db: Session, seller_id: int) -> Dict[str, Any]:
    seller = db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()
    if not seller:
        return {"seller_id": seller_id, "error": "seller_not_found"}

    orders = db.query(Order).filter(Order.seller_id == seller_id).all()
    summary = {
        "seller_id": seller_id,
        "seller_name": seller.seller_name,
        "total_orders": len(orders),
        "created": sum(1 for order in orders if order.status == "created"),
        "accepted": sum(1 for order in orders if order.status == "accepted"),
        "ready_for_pickup": sum(1 for order in orders if order.status == "ready_for_pickup"),
        "picked_up": sum(1 for order in orders if order.status == "picked_up"),
        "failed": sum(1 for order in orders if order.status == "failed"),
    }

    emit_event(
        event_name="seller.summary.generated",
        entity_type="seller",
        entity_id=seller_id,
        actor_role="system",
        source="analytics",
        metadata={"total_orders": summary["total_orders"]},
    )

    return summary


def platform_overview(db: Session) -> Dict[str, Any]:
    sellers = db.query(SellerProfile).count()
    orders = db.query(Order).count()
    active = db.query(Order).filter(Order.status.in_(["created", "validated", "accepted", "preparing", "ready_for_pickup", "pickup_verification_pending"])).count()
    exception_count = db.query(ExceptionCase).filter(ExceptionCase.status == "open").count()

    return {
        "seller_count": sellers,
        "order_count": orders,
        "active_orders": active,
        "open_exceptions": exception_count,
        "status_breakdown": {
            "created": db.query(Order).filter(Order.status == "created").count(),
            "accepted": db.query(Order).filter(Order.status == "accepted").count(),
            "ready_for_pickup": db.query(Order).filter(Order.status == "ready_for_pickup").count(),
            "picked_up": db.query(Order).filter(Order.status == "picked_up").count(),
            "failed": db.query(Order).filter(Order.status == "failed").count(),
        },
    }
