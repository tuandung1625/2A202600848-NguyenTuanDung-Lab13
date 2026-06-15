# Grading Evidence

## Submission Identity

- Student: Nguyễn Tuấn Dũng
- Student ID: `2A202600848`
- Repository: <https://github.com/tuandung1625/Lab13-Observability>
- Final report: `docs/blueprint.md`

## Reproducible Checks

Run the API before collecting runtime evidence:

```powershell
python -m uvicorn app.main:app --reload --env-file .env
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
```

Optional evidence exporters:

```powershell
python scripts/export_log_evidence.py
python scripts/verify_langfuse.py --minutes 120 --minimum 10 --output docs/evidence/langfuse-summary.json
python scripts/incident_demo.py --output docs/evidence/incident-results.json
python -m pytest -q
```

## Required Evidence Checklist

| Evidence | Expected location | Status in this checkout |
|---|---|---|
| Correlation ID and PII-redacted JSON logs | `docs/evidence/log-samples.html` or screenshot | Regenerate from runtime logs |
| Langfuse trace count and waterfall | `docs/evidence/langfuse-summary.html` or screenshot | Requires valid Langfuse credentials |
| Six-panel dashboard | `docs/evidence/dashboard.png` | Capture manually from `/` |
| Alert rules and runbook links | `config/alert_rules.yaml`, `docs/alerts.md`, `/runbooks` | Present in source |
| Incident metrics | `docs/evidence/incident-results.json` | Regenerate while API is running |
| Automated tests | Terminal output from `python -m pytest -q` | Requires installed `pytest` |

Generated runtime logs, credentials, and local environment files must not be
committed. Evidence files may be committed under `docs/evidence/` when required
for grading.

## Git Evidence

| Commit | Contribution |
|---|---|
| [`060547b412e85f5f84bc47e41afc8716c4caef1a`](https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13/commit/060547b412e85f5f84bc47e41afc8716c4caef1a),  | Structured logging, correlation middleware, PII protection, and audit logging |
| [`0488733469a101e53a8d1f8a6f7bef39d50d2464`](https://github.com/tuandung1625/2A202600848-NguyenTuanDung-Lab13/commit/0488733469a101e53a8d1f8a6f7bef39d50d2464),  |

## Current Verification Note

On June 15, 2026, this checkout did not contain `data/logs.jsonl` and neither
the system Python nor `.venv` had `pytest` installed. Therefore log validation
and tests could not be rerun during the documentation pass. Historical runtime
measurements recorded in `docs/blueprint.md` are labeled as recorded evidence,
not newly reproduced results.
