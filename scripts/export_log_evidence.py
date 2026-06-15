from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export sanitized structured log evidence")
    parser.add_argument("--logs", type=Path, default=Path("data/logs.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/log-samples.json"))
    args = parser.parse_args()

    records = [json.loads(line) for line in args.logs.read_text(encoding="utf-8").splitlines() if line.strip()]
    api_records = [record for record in records if record.get("service") == "api"]
    pii_record = next(record for record in api_records if "[REDACTED_" in json.dumps(record))
    response_record = next(record for record in api_records if record.get("event") == "response_sent")
    samples = {"pii_redaction": pii_record, "correlation_and_enrichment": response_record}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(samples, indent=2) + "\n", encoding="utf-8")
    sections = "".join(
        f"<section><h2>{html.escape(name.replace('_', ' ').title())}</h2><pre>{html.escape(json.dumps(record, indent=2))}</pre></section>"
        for name, record in samples.items()
    )
    page = f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>Structured Log Evidence</title>
<style>body{{font:16px Segoe UI,Arial;background:#07111f;color:#edf5ff;max-width:1300px;margin:auto;padding:30px}}section{{background:#101e31;border:1px solid #29405d;border-radius:14px;padding:20px;margin:16px 0}}pre{{white-space:pre-wrap;color:#bfe0ff;background:#091523;padding:18px;border-radius:10px}}h1{{margin-bottom:4px}}p{{color:#91a4ba}}</style></head><body><h1>Structured Logging Evidence</h1><p>Correlation propagation, context enrichment, and PII redaction.</p>{sections}</body></html>"""
    args.output.with_suffix(".html").write_text(page, encoding="utf-8")
    print(f"Exported {len(samples)} log samples to {args.output}")


if __name__ == "__main__":
    main()