from __future__ import annotations

ORDER_VALID_TRANSITIONS = {
    "created": {"validated", "cancelled"},
    "validated": {"accepted", "rejected", "cancelled"},
    "accepted": {"preparing", "cancelled"},
    "rejected": {"cancelled"},
    "preparing": {"ready_for_pickup", "cancelled", "delayed"},
    "ready_for_pickup": {"pickup_verification_pending", "cancelled", "failed"},
    "pickup_verification_pending": {"picked_up", "failed"},
    "picked_up": {"completed"},
    "delayed": {"ready_for_pickup", "cancelled", "failed"},
    "failed": {"refund_pending", "cancelled"},
    "completed": set(),
    "cancelled": set(),
    "refund_pending": {"refunded"},
    "refunded": set(),
}


def assert_valid_transition(current_status: str, next_status: str) -> bool:
    allowed = ORDER_VALID_TRANSITIONS.get(current_status, set())
    if next_status not in allowed:
        raise ValueError(
            f"Invalid status transition from '{current_status}' to '{next_status}'. "
            f"Allowed transitions: {sorted(allowed)}"
        )
    return True
