# Alert Rules and Runbooks

The canonical thresholds and intended durations are defined in
`config/alert_rules.yaml`. The lab runtime evaluator in `app/alerts.py` compares
the current in-memory snapshot with each threshold; it does not persist or
enforce the `5m` or `1m` duration. The dashboard links each alert to the
matching section on `/runbooks`.

## 1. High Latency P95

- Alert: `high_latency_p95`
- Severity: P2
- Owner: `team-oncall`
- Trigger: `latency_p95_ms > 3000 for 5m`
- Impact: Tail latency breaches the 3000 ms SLO and users wait too long for a response.
- Likely lab cause: The `rag_slow` incident adds delay to retrieval.

First checks:

1. Open a slow `agent_run` trace from the last hour.
2. Compare the duration of `rag_retrieval` with `llm_generation`.
3. Check `GET /health` to see whether `rag_slow` is enabled.
4. Correlate the trace with structured logs using `correlation_id`.

Mitigation:

- Disable `rag_slow`.
- Add a retrieval timeout and return a controlled fallback response.
- Route retrieval to a fallback source when the primary source is unhealthy.
- Reduce oversized queries or retrieved context where appropriate.

Verification:

- Send normal requests again and confirm P95 returns below 3000 ms.
- Confirm the alert is no longer firing at `GET /alerts`.

## 2. High Error Rate

- Alert: `high_error_rate`
- Severity: P1
- Owner: `team-oncall`
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: Users receive failed responses.
- Likely lab cause: The `tool_fail` incident raises `RuntimeError` during retrieval.

First checks:

1. Inspect `error_breakdown` at `GET /metrics`.
2. Group structured logs by `error_type` and `correlation_id`.
3. Inspect the failed trace to locate the failing operation.
4. Check `GET /health` to see whether `tool_fail` is enabled.

Mitigation:

- Disable `tool_fail`.
- Add bounded retries only for transient failures.
- Use a fallback retrieval source or a controlled degraded response.
- Roll back a recent change if failures began after deployment.

Verification:

- Send successful requests and confirm the error rate trends below 5%.
- Confirm no new `RuntimeError` records appear.

## 3. Cost Budget Spike

- Alert: `cost_budget_spike`
- Severity: P2
- Owner: `finops-owner`
- Trigger: `max_cost_usd > 0.005 for 1m`
- Impact: A single expensive request can accelerate budget burn.
- Likely lab cause: The `cost_spike` incident multiplies output tokens by five.

First checks:

1. Compare `tokens_in` and `tokens_out` for expensive requests.
2. Inspect generation metadata and group traces by feature and model.
3. Check `GET /health` to see whether `cost_spike` is enabled.
4. Compare `max_cost_usd` and `total_cost_usd` at `GET /metrics`.

Mitigation:

- Disable `cost_spike`.
- Cap output tokens and shorten prompts or retrieved context.
- Route simple requests to a cheaper model.
- Cache reusable prompt or retrieval results where safe.

Verification:

- Confirm new requests stay at or below `$0.005` per request.
- Confirm the alert is no longer firing at `GET /alerts`.

## Lab Alert Test

Run the API, then execute:

```powershell
python scripts/incident_demo.py --output docs/evidence/incident-results.json
```

The script enables each incident, records metrics and firing alerts, and then
disables the incident. A short incident may not cross every threshold. Metrics
are process-local, so restart the API when a clean baseline is required.
