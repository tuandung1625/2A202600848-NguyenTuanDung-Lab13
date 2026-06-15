from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all three lab incidents")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    results = []
    payload = {"user_id": "incident-user", "session_id": "incident-demo", "feature": "qa", "message": "Explain monitoring and alerts"}
    with httpx.Client(timeout=20.0) as client:
        for scenario in ["rag_slow", "tool_fail", "cost_spike"]:
            client.post(f"{args.base_url}/incidents/{scenario}/enable").raise_for_status()
            response = client.post(f"{args.base_url}/chat", json=payload)
            metrics = client.get(f"{args.base_url}/metrics").json()
            alerts = client.get(f"{args.base_url}/alerts").json()
            client.post(f"{args.base_url}/incidents/{scenario}/disable").raise_for_status()
            results.append(
                {
                    "scenario": scenario,
                    "status_code": response.status_code,
                    "latency_p95_ms": metrics["latency_p95_ms"],
                    "error_rate_pct": metrics["error_rate_pct"],
                    "max_cost_usd": metrics["max_cost_usd"],
                    "firing_alerts": [rule["name"] for rule in alerts if rule["firing"]],
                }
            )

    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()