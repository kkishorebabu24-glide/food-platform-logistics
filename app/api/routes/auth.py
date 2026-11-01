from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import create_token, get_current_user
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    role: str = "buyer"
    user_id: Optional[int] = None


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        user = User(email=payload.email, role=payload.role, status="active", password_hash="demo-user")
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.role = payload.role
        db.commit()

    token = create_token(user.id, user.email, user.role)
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
