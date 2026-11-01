from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


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
