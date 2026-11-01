from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, default="buyer")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    resident_profile = relationship("ResidentProfile", back_populates="user", uselist=False)
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False)


class ResidentProfile(Base):
    __tablename__ = "resident_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    flat_number = Column(String, nullable=False)
    building_id = Column(String, nullable=False)
    trust_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resident_profile")


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    seller_name = Column(String, nullable=False)
    verification_status = Column(String, default="pending")
    menu_status = Column(String, default="draft")
    capacity_profile = Column(String, default="standard")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="seller_profile")
    menus = relationship("MenuItem", back_populates="seller")
    orders = relationship("Order", back_populates="seller")
    batches = relationship("FulfillmentBatch", back_populates="seller")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, default=0.0)
    available = Column(Boolean, default=True)
    prep_time_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("SellerProfile", back_populates="menus")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), index=True, nullable=False)
    status = Column(String, default="created")
    requested_slot = Column(String, nullable=True)
    assigned_batch_id = Column(Integer, ForeignKey("fulfillment_batches.id"), nullable=True)
    subtotal = Column(Float, default=0.0)
    payment_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("SellerProfile", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    pickup = relationship("PickupSession", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")


class SellerCapacity(Base):
    __tablename__ = "seller_capacities"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), nullable=False, index=True)
    slot_start = Column(String, nullable=False)
    slot_end = Column(String, nullable=False)
    max_orders = Column(Integer, default=20)
    active_order_count = Column(Integer, default=0)
    status = Column(String, default="open")


class FulfillmentBatch(Base):
    __tablename__ = "fulfillment_batches"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), nullable=False, index=True)
    status = Column(String, default="batch_created")
    prep_window_start = Column(String, nullable=True)
    prep_window_end = Column(String, nullable=True)
    ready_time = Column(String, nullable=True)
    pickup_window_start = Column(String, nullable=True)
    pickup_window_end = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("SellerProfile", back_populates="batches")


class PickupSession(Base):
    __tablename__ = "pickup_sessions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("seller_profiles.id"), nullable=False, index=True)
    pickup_time = Column(DateTime, nullable=True)
    verification_code = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="pickup")


class ExceptionCase(Base):
    __tablename__ = "exception_cases"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    batch_id = Column(Integer, ForeignKey("fulfillment_batches.id"), nullable=True, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, default="medium")
    status = Column(String, default="open")
    raised_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="history")
