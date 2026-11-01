from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.order_service import create_order, get_order_by_id, list_orders, update_order_status

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order_route(payload: OrderCreate, db: Session = Depends(get_db)):
    try:
        return create_order(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("")
def list_orders_route(db: Session = Depends(get_db)):
    return list_orders(db)


@router.get("/{order_id}")
def get_order_route(order_id: int, db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/{order_id}/status")
def update_order_status_route(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    try:
        order = update_order_status(db, order_id, payload.status, payload.reason)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
