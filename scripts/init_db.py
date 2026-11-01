from __future__ import annotations

from datetime import datetime
from pathlib import Path


def init_db() -> None:
    from app.db.database import Base, engine
    from app.db.models import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print(f"[{datetime.utcnow().isoformat()}] Database initialized")


if __name__ == "__main__":
    init_db()
