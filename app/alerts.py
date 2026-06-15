from __future__ import annotations

from typing import Any


def evaluate_alerts(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rules = [
        {
            "name": "high_latency_p95",
            "severity": "P2",
            "metric": "latency_p95_ms",
            "value": metrics["latency_p95_ms"],
            "threshold": 3000.0,
            "unit": "ms",
            "runbook": "/runbooks#high-latency-p95",
        },
        {
            "name": "high_error_rate",
            "severity": "P1",
            "metric": "error_rate_pct",
            "value": metrics["error_rate_pct"],
            "threshold": 5.0,
            "unit": "%",
            "runbook": "/runbooks#high-error-rate",
        },
        {
            "name": "cost_budget_spike",
            "severity": "P2",
            "metric": "max_cost_usd",
            "value": metrics["max_cost_usd"],
            "threshold": 0.005,
            "unit": "USD/request",
            "runbook": "/runbooks#cost-budget-spike",
        },
    ]
    for rule in rules:
        rule["firing"] = rule["value"] > rule["threshold"]
    return rules