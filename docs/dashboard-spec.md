# Dashboard Specification

## Purpose

The Layer-2 dashboard provides a compact view of service health and AI workload
signals. It is served by the FastAPI application at `http://127.0.0.1:8000/`.

## Main Panels

| Panel | Metrics | Unit | Threshold or target |
|---|---|---|---|
| Latency | `latency_p50_ms`, `latency_p95_ms`, `latency_p99_ms` | ms | P95 `< 3000 ms` |
| Traffic | `traffic`, `requests_per_minute` | requests | Operational volume |
| Error rate | `error_rate_pct`, `error_breakdown` | percent and count by type | `< 2%` SLO; alert at `> 5%` |
| Cost | `total_cost_usd`, `max_cost_usd` | USD | Daily budget `< $2.50`; alert at `> $0.005/request` |
| Tokens | `tokens_in_total`, `tokens_out_total` | tokens | Watch output-token growth |
| Quality proxy | `quality_avg` | score from 0 to 1 | `>= 0.75` |

## Display Behavior

- Main layer contains exactly six panels.
- Header labels the view as the last one hour.
- Browser refresh interval is 15 seconds.
- Every panel labels its unit and operational threshold or target.
- Alert badges are loaded from `GET /alerts`.
- Firing alert badges link to the matching section on `/runbooks`.
- Layout adapts from three columns to one column on smaller screens.

## Data Sources and Limitations

The dashboard reads `GET /metrics`, backed by the in-memory aggregator in
`app/metrics.py`. Percentiles and totals cover the current application process,
not a durable one-hour database window. The chart displays at most the latest
60 recorded events. Restarting the API resets all metrics.

The current implementation is suitable for the lab demonstration. A production
version should export metrics to a durable monitoring backend and calculate
time-windowed SLOs and alert durations there.

## Verification

1. Start the API and send requests with `scripts/load_test.py`.
2. Open `/` and confirm that six cards are visible.
3. Enable an incident and generate enough load to cross its threshold.
4. Open the badge and confirm it resolves to the correct `/runbooks` section.
5. Capture the completed dashboard as `docs/evidence/dashboard.png`.
