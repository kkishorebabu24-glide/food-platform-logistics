from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime


def emit_event(
    *,
    event_name: str,
    entity_type: str,
    entity_id: int,
    actor_id: Optional[int] = None,
    actor_role: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    source: str = "api",
) -> Dict[str, Any]:
    event = {
        "event_id": f"evt-{int(datetime.utcnow().timestamp() * 1000)}-{entity_id}",
        "event_name": event_name,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "metadata": metadata or {},
    }
    return event
