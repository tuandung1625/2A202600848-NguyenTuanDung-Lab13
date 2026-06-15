from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from .pii import scrub_data

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))
_LOG_LOCK = threading.Lock()

class JsonlFileProcessor:
    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        rendered = structlog.processors.JSONRenderer()(logger, method_name, event_dict)
        with _LOG_LOCK, LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(rendered + "\n")
        return event_dict



def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    return scrub_data(event_dict)


def add_schema_defaults(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    event_dict.setdefault("service", os.getenv("APP_NAME", "day13-observability-lab"))
    event_dict.setdefault("env", os.getenv("APP_ENV", "dev"))
    event_dict.setdefault("correlation_id", "system")
    return event_dict



def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
    structlog.configure(
        processors=[
            merge_contextvars,
            add_schema_defaults,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
            scrub_event,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            JsonlFileProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )



def get_logger() -> structlog.typing.FilteringBoundLogger:
    return structlog.get_logger()
