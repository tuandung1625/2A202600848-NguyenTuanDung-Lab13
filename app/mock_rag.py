from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    if "refund" in lowered:
        return CORPUS["refund"]
    if any(keyword in lowered for keyword in ["monitoring", "metrics", "traces", "latency", "alerts"]):
        return CORPUS["monitoring"]
    if any(keyword in lowered for keyword in ["policy", "pii", "sensitive", "app logs"]):
        return CORPUS["policy"]
    return ["No domain document matched. Use general fallback answer."]
