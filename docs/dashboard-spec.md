# Dashboard Spec

Required Layer-2 panels:
1. Latency P50/P95/P99
2. Traffic (request count or QPS)
3. Error rate with breakdown
4. Cost over time
5. Tokens in/out
6. Quality proxy (heuristic, thumbs, or regenerate rate)

Quality bar:
- default time range = 1 hour
- auto refresh every 15-30 seconds
- visible threshold/SLO line
- units clearly labeled
- no more than 6-8 panels on the main layer


## Implemented dashboard

The live dashboard is served at `http://127.0.0.1:8000/` and implements exactly six panels:

1. Latency P50/P95/P99 with the 3000ms P95 SLO
2. Total traffic and requests per minute
3. Error rate and error-type breakdown
4. Total and maximum per-request cost
5. Input and output token totals
6. Average heuristic quality score with the 0.75 target

It uses a one-hour label, refreshes every 15 seconds, renders short time-series lines, and links firing alert badges to `/runbooks`. Evidence: `docs/evidence/dashboard.png`.