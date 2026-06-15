# Day 13 Observability Lab Report

> Completed machine-readable submission. See `docs/blueprint.md` for the
> detailed explanations, limitations, and reproduction notes.

## 1. Team Metadata

- [GROUP_NAME]: Solo Observability Lab
- [REPO_URL]: https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13
- [STUDENT_ID]: 2A202600848
- [MEMBERS]:
  - Member A: Nguyễn Tuấn Dũng | Student ID: 2A202600848 | Role: All roles

---

## 2. Group Performance (Auto-Verified)

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100 (recorded lab run)
- [TOTAL_TRACES_COUNT]: 14 traces in a 120-minute window on June 15, 2026
- [PII_LEAKS_FOUND]: 0 in the recorded validation run

---

## 3. Technical Evidence (Group)

### 3.1 Logging and Tracing

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: `docs/evidence/log-samples.html`
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: `docs/evidence/log-samples.html`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: `docs/evidence/langfuse-summary.html`
- [TRACE_WATERFALL_EXPLANATION]: The `agent_run` root contains `rag_retrieval` and `llm_generation`. During `rag_slow`, retrieval dominated total latency, localizing the bottleneck to RAG. Raw input/output capture is disabled and trace metadata uses hashed or scrubbed values.

### 3.2 Dashboard and SLOs

- [DASHBOARD_6_PANELS_SCREENSHOT]: `docs/evidence/dashboard.png`
- [SLO_TABLE]:

| SLI | Target | Window | Recorded value |
|---|---:|---|---:|
| Latency P95 | `< 3000 ms` | 28d objective | 154 ms baseline; 3651 ms during `rag_slow` |
| Error rate | `< 2%` | 28d objective | 0% baseline; 33.33% during incidents |
| Cost budget | `< $2.50/day` | 1d | $0.022056 for 10 baseline requests |
| Quality score | `>= 0.75` | 1d | 0.87 baseline |

### 3.3 Alerts and Runbook

- [ALERT_RULES_SCREENSHOT]: `config/alert_rules.yaml` and `docs/alerts.md`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`

---

## 4. Incident Response (Group)

- [SCENARIO_NAME]: `rag_slow`, `tool_fail`, and `cost_spike`
- [SYMPTOMS_OBSERVED]: P95 reached 3651 ms; `tool_fail` returned HTTP 500 with `RuntimeError`; maximum request cost reached $0.009621.
- [ROOT_CAUSE_PROVED_BY]: Trace `46f6009a787411db6b09935af78ecb65`, correlated structured logs, and token/cost metrics.
- [FIX_ACTION]: Disable the incident; add retrieval timeout/fallback and tool error handling; cap output tokens or route to a cheaper model.
- [PREVENTIVE_MEASURE]: Alert on P95, error rate, and request cost; retain correlation IDs, PII scrubbing, safe trace metadata, audit logs, and tested runbooks.

---

## 5. Individual Contributions and Evidence

### [MEMBER_A_NAME]: Nguyễn Tuấn Dũng
- [STUDENT_ID]: 2A202600848
- [TASKS_COMPLETED]: Structured logging, correlation IDs, recursive PII scrubbing, Langfuse tracing, RAG/LLM observations, metrics, six-panel dashboard, SLOs, alerts, runbooks, incidents, audit logs, tests, evidence scripts, and report.
- [EVIDENCE_LINK]: [`060547b412e85f5f84bc47e41afc8716c4caef1a`](https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13/commit/060547b412e85f5f84bc47e41afc8716c4caef1a), [`0488733469a101e53a8d1f8a6f7bef39d50d2464`](https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13/commit/0488733469a101e53a8d1f8a6f7bef39d50d2464), 

### [MEMBER_B_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; covered by Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_C_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; covered by Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_D_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; covered by Member A.
- [EVIDENCE_LINK]: N/A

### [MEMBER_E_NAME]: N/A
- [TASKS_COMPLETED]: Individual submission; covered by Member A.
- [EVIDENCE_LINK]: N/A

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: Token and cost metrics identify output-token spikes; mitigations are documented in `docs/alerts.md`.
- [BONUS_AUDIT_LOGS]: Chat and incident-control actions are written to PII-scrubbed `data/audit.jsonl`.
- [BONUS_CUSTOM_METRIC]: `/metrics` exposes quality, maximum cost, requests per minute, error breakdown, and recent event series.
