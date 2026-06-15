from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pii import scrub_data

AUDIT_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))
_AUDIT_LOCK = threading.Lock()


def write_audit(event: str, correlation_id: str, actor_hash: str, payload: dict[str, Any]) -> None:
    record = scrub_data(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "correlation_id": correlation_id,
            "actor_hash": actor_hash,
            "payload": payload,
        }
    )
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _AUDIT_LOCK, AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")