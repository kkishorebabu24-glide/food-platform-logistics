from __future__ import annotations

from app.db.database import SessionLocal
from app.db.models import SellerProfile, User


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        buyer = db.query(User).filter(User.email == "buyer@demo.local").first()
        if buyer is None:
            buyer = User(email="buyer@demo.local", phone="9999999999", role="buyer", status="active", password_hash="demo")
            db.add(buyer)
            db.flush()

        seller = db.query(User).filter(User.email == "seller@demo.local").first()
        if seller is None:
            seller = User(email="seller@demo.local", phone="8888888888", role="seller", status="active", password_hash="demo")
            db.add(seller)
            db.flush()

        seller_profile = db.query(SellerProfile).filter(SellerProfile.user_id == seller.id).first()
        if seller_profile is None:
            seller_profile = SellerProfile(
                user_id=seller.id,
                seller_name="Demo Seller",
                verification_status="approved",
                menu_status="active",
                capacity_profile="standard",
            )
            db.add(seller_profile)
            db.commit()
        else:
            db.commit()

        print("Demo data seeded")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
