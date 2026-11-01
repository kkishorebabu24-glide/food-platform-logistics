from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: float = 0.0


class OrderCreate(BaseModel):
    buyer_id: int
    seller_id: int
    requested_slot: Optional[str] = None
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class OrderRead(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    status: str
    requested_slot: Optional[str]
    subtotal: float

    model_config = {"from_attributes": True}
