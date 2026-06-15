from __future__ import annotations

from collections import Counter, deque
from datetime import datetime, timedelta, timezone
from statistics import mean
from threading import Lock
from typing import Any

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
EVENTS: deque[dict[str, Any]] = deque(maxlen=500)
_LOCK = Lock()


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    with _LOCK:
        TRAFFIC += 1
        REQUEST_LATENCIES.append(latency_ms)
        REQUEST_COSTS.append(cost_usd)
        REQUEST_TOKENS_IN.append(tokens_in)
        REQUEST_TOKENS_OUT.append(tokens_out)
        QUALITY_SCORES.append(quality_score)
        EVENTS.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "quality_score": quality_score,
                "error": False,
            }
        )


def record_error(error_type: str) -> None:
    global TRAFFIC
    with _LOCK:
        TRAFFIC += 1
        ERRORS[error_type] += 1
        EVENTS.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "latency_ms": 0,
                "cost_usd": 0.0,
                "tokens_in": 0,
                "tokens_out": 0,
                "quality_score": 0.0,
                "error": True,
                "error_type": error_type,
            }
        )

def snapshot() -> dict[str, Any]:
    with _LOCK:
        error_count = sum(ERRORS.values())
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        recent_count = sum(datetime.fromisoformat(event["ts"]) >= one_minute_ago for event in EVENTS)
        return {
            "traffic": TRAFFIC,
            "requests_per_minute": recent_count,
            "latency_p50_ms": percentile(REQUEST_LATENCIES, 50),
            "latency_p95_ms": percentile(REQUEST_LATENCIES, 95),
            "latency_p99_ms": percentile(REQUEST_LATENCIES, 99),
            "error_rate_pct": round((error_count / TRAFFIC) * 100, 2) if TRAFFIC else 0.0,
            "error_breakdown": dict(ERRORS),
            "avg_cost_usd": round(mean(REQUEST_COSTS), 6) if REQUEST_COSTS else 0.0,
            "max_cost_usd": round(max(REQUEST_COSTS), 6) if REQUEST_COSTS else 0.0,
            "total_cost_usd": round(sum(REQUEST_COSTS), 6),
            "tokens_in_total": sum(REQUEST_TOKENS_IN),
            "tokens_out_total": sum(REQUEST_TOKENS_OUT),
            "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
            "time_series": list(EVENTS)[-60:],
        }

def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])

def reset() -> None:
    global TRAFFIC
    with _LOCK:
        TRAFFIC = 0
        REQUEST_LATENCIES.clear()
        REQUEST_COSTS.clear()
        REQUEST_TOKENS_IN.clear()
        REQUEST_TOKENS_OUT.clear()
        ERRORS.clear()
        QUALITY_SCORES.clear()
        EVENTS.clear()