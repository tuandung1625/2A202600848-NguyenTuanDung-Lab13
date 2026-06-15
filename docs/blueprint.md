# Day 13 Observability Lab Report

> **Submission type**: Individual project. Machine-readable tags are preserved.

## 1. Team Metadata

- [GROUP_NAME]: Solo Observability Lab
- [REPO_URL]: https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13
- [STUDENT_ID]: 2A202600848
- [MEMBERS]:
  - Member A: Nguyễn Tuấn Dũng | Student ID: 2A202600848 | Role: All roles

---

## 2. Group Performance (Auto-Verified)

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100 (recorded during the completed lab run)
- [TOTAL_TRACES_COUNT]: 14 traces in a 120-minute window on June 15, 2026
- [PII_LEAKS_FOUND]: 0 in the recorded validation run

Reproduction commands and the current-checkout limitations are documented in
`docs/grading-evidence.md`.

---

## 3. Technical Evidence (Group)

### 3.1 Logging and Tracing

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: `docs/evidence/log-samples.html` (regenerate with `scripts/export_log_evidence.py`)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: `docs/evidence/log-samples.html` (regenerate with `scripts/export_log_evidence.py`)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: `docs/evidence/langfuse-summary.html` or the linked live Langfuse trace
- [TRACE_WATERFALL_EXPLANATION]: The `agent_run` root observation contains `rag_retrieval` and `llm_generation`. In the recorded `rag_slow` run, retrieval dominated total latency while generation remained near its normal duration, localizing the bottleneck to RAG. Raw prompt and response capture is disabled; traces contain hashed user identity, session, feature/model tags, scrubbed previews, token usage, and safe metadata.

### 3.2 Dashboard and SLOs

- [DASHBOARD_6_PANELS_SCREENSHOT]: `docs/evidence/dashboard.png` (capture from `http://127.0.0.1:8000/`)
- [SLO_TABLE]:

| SLI | Target | Window | Recorded value |
|---|---:|---|---:|
| Latency P95 | `< 3000 ms` | 28d objective | 154 ms baseline; 3651 ms during `rag_slow` |
| Error rate | `< 2%` | 28d objective | 0% baseline; 33.33% during the incident sequence |
| Cost budget | `< $2.50/day` | 1d | $0.022056 for the 10-request baseline |
| Quality score | `>= 0.75` | 1d | 0.87 baseline |

The lab dashboard uses process-local metrics. Its header shows one hour, while
the actual totals cover the current process and charts retain the latest 60
events. This limitation is documented in `docs/dashboard-spec.md`.

### 3.3 Alerts and Runbook

- [ALERT_RULES_SCREENSHOT]: `config/alert_rules.yaml` and `docs/alerts.md`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`

The three implemented alerts are high P95 latency, high error rate, and
per-request cost spike. Runtime alert badges link to `/runbooks`.

---

## 4. Incident Response (Group)

- [SCENARIO_NAME]: `rag_slow`, `tool_fail`, and `cost_spike`
- [SYMPTOMS_OBSERVED]: The recorded run showed P95 latency at 3651 ms for `rag_slow`; `tool_fail` returned HTTP 500 with `RuntimeError`; `cost_spike` raised maximum request cost to $0.009621.
- [ROOT_CAUSE_PROVED_BY]: Trace `46f6009a787411db6b09935af78ecb65` separated RAG and LLM timings. Structured logs recorded `RuntimeError` for retrieval failure. Token and cost metrics isolated the output-token increase. The incident script can regenerate `docs/evidence/incident-results.json`.
- [FIX_ACTION]: Disable the active incident; add a retrieval timeout and fallback; handle tool failures with a degraded response; cap output tokens or route simple requests to a cheaper model.
- [PREVENTIVE_MEASURE]: Alert on P95 latency, error rate, and maximum request cost; retain correlation IDs, PII scrubbing, trace metadata, audit logs, and tested runbooks.

Debugging flow:

1. Use dashboard metrics to identify the affected service signal.
2. Use traces to locate the slow or failing operation.
3. Use correlated structured logs to confirm the error and request context.

---

## 5. Individual Contributions and Evidence

### [MEMBER_A_NAME]: Nguyễn Tuấn Dũng

- [STUDENT_ID]: 2A202600848
- [TASKS_COMPLETED]: Implemented structured JSON logging, validated correlation IDs, recursive PII scrubbing, hashed user identity, separate audit logs, Langfuse tracing, RAG/LLM observations, in-memory metrics, six-panel dashboard, SLO and alert configuration, runbooks, incident controls, automated tests, evidence scripts, and this report.
- [EVIDENCE_LINK]: [`4a2b50a`](https://github.com/tuandung1625/Lab13-Observability/commit/4a2b50a), [`83848a4`](https://github.com/tuandung1625/Lab13-Observability/commit/83848a4), [`5b57a6c`](https://github.com/tuandung1625/Lab13-Observability/commit/5b57a6c)

### [MEMBER_B_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; all work is listed under Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_C_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; all work is listed under Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_D_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; all work is listed under Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_E_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; all work is listed under Member A.
- [EVIDENCE_LINK]: N/A

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: Output-token and maximum-cost metrics localize cost spikes. The runbook recommends token caps, shorter context, caching, and cheaper model routing.
- [BONUS_AUDIT_LOGS]: Successful chat actions and incident-control actions are written to the separate, PII-scrubbed `data/audit.jsonl`.
- [BONUS_CUSTOM_METRIC]: `/metrics` exposes heuristic `quality_avg`, maximum request cost, requests per minute, error breakdown, and a recent event time series. Incident and Langfuse verification are automated by scripts.
