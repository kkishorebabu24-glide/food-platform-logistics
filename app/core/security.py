from __future__ import annotations

from fastapi import HTTPException, status


def require_role(role: str):
    def _validator() -> None:
        # Placeholder for future JWT/role enforcement.
        return None

    return _validator


def verify_token() -> None:
    # Placeholder for future auth validation.
    return None
