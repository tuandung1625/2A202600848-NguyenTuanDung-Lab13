from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from langfuse import get_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify recent Langfuse traces for the lab")
    parser.add_argument("--minutes", type=int, default=60)
    parser.add_argument("--minimum", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    load_dotenv()
    since = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)
    client = get_client()
    traces = client.api.trace.list(limit=100, tags="lab", from_timestamp=since)
    latest_observations = []
    if traces.data:
        observations = client.api.observations.get_many(limit=100, trace_id=traces.data[0].id)
        latest_observations = [
            {
                "id": observation.id,
                "name": observation.name,
                "type": getattr(observation.type, "value", str(observation.type)),
                "parent_observation_id": observation.parent_observation_id,
            }
            for observation in observations.data
        ]
    summary = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "window_minutes": args.minutes,
        "trace_count": len(traces.data),
        "minimum_required": args.minimum,
        "passed": len(traces.data) >= args.minimum,
        "latest_trace_ids": [trace.id for trace in traces.data[:10]],
        "latest_trace_url": client.get_trace_url(trace_id=traces.data[0].id) if traces.data else None,
        "latest_trace_observations": latest_observations,
    }
    rendered = json.dumps(summary, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        rows = "".join(f"<li><code>{html.escape(trace_id)}</code></li>" for trace_id in summary["latest_trace_ids"])
        observations_html = "".join(
            f"<tr><td>{html.escape(item['name'])}</td><td>{html.escape(item['type'])}</td><td><code>{html.escape(str(item['parent_observation_id']))}</code></td></tr>"
            for item in latest_observations
        )
        evidence_html = f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>Langfuse Evidence</title>
<style>body{{font:16px Segoe UI,Arial;background:#07111f;color:#edf5ff;max-width:1100px;margin:auto;padding:36px}}.hero{{display:flex;justify-content:space-between;align-items:end}}.count{{font-size:64px;color:#42d6a4;font-weight:700}}section{{background:#101e31;border:1px solid #29405d;border-radius:14px;padding:22px;margin:18px 0}}code{{color:#6eb4ff}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #29405d}}a{{color:#6eb4ff}}</style></head><body>
<div class=\"hero\"><div><h1>Langfuse Trace Verification</h1><p>Window: last {args.minutes} minutes</p></div><div class=\"count\">{summary['trace_count']} traces</div></div>
<section><h2>Passing criterion</h2><p>Required: {args.minimum} traces. Result: <strong>{'PASSED' if summary['passed'] else 'FAILED'}</strong></p><p><a href=\"{html.escape(summary['latest_trace_url'] or '#')}\">Open latest trace in Langfuse</a></p></section>
<section><h2>Latest trace waterfall</h2><table><tr><th>Observation</th><th>Type</th><th>Parent observation</th></tr>{observations_html}</table></section>
<section><h2>Recent trace IDs</h2><ol>{rows}</ol></section></body></html>"""
        args.output.with_suffix(".html").write_text(evidence_html, encoding="utf-8")
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()