from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class BatchCreate(BaseModel):
    seller_id: int
    prep_window_start: Optional[str] = None
    prep_window_end: Optional[str] = None
    ready_time: Optional[str] = None
    pickup_window_start: Optional[str] = None
    pickup_window_end: Optional[str] = None


class BatchRead(BaseModel):
    id: int
    seller_id: int
    status: str
    ready_time: Optional[str]
    pickup_window_start: Optional[str]
    pickup_window_end: Optional[str]

    model_config = {"from_attributes": True}


class PickupVerify(BaseModel):
    order_id: int
    buyer_id: int
    seller_id: Optional[int] = None


class PickupRead(BaseModel):
    id: int
    order_id: int
    buyer_id: int
    seller_id: int
    verification_code: Optional[str]
    status: str

    model_config = {"from_attributes": True}
