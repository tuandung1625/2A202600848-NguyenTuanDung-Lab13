import json

from fastapi.testclient import TestClient

from app import logging_config, metrics
from app.incidents import STATE
from app.main import app


def test_chat_propagates_context_and_scrubs_pii(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "logs.jsonl"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)
    monkeypatch.setattr("app.audit.AUDIT_PATH", audit_path)
    metrics.reset()

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "demo-request"},
            json={
                "user_id": "student@vinuni.edu.vn",
                "session_id": "session-1",
                "feature": "qa",
                "message": "Refund for student@vinuni.edu.vn, card 4111 1111 1111 1111",
            },
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "demo-request"
    assert response.json()["correlation_id"] == "demo-request"
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    assert all(record["correlation_id"] == "demo-request" for record in api_records)
    assert all({"user_id_hash", "session_id", "feature", "model", "env"} <= record.keys() for record in api_records)
    assert "student@" not in log_path.read_text(encoding="utf-8")
    assert "4111" not in log_path.read_text(encoding="utf-8")
    assert audit_path.exists()


def test_dashboard_metrics_and_alerts() -> None:
    metrics.reset()
    metrics.record_request(3501, 0.007, 100, 500, 0.8)
    metrics.record_error("RuntimeError")

    with TestClient(app) as client:
        dashboard = client.get("/")
        metric_response = client.get("/metrics")
        alerts = client.get("/alerts").json()

    assert dashboard.status_code == 200
    assert dashboard.text.count('class="card"') == 6
    assert metric_response.json()["error_rate_pct"] == 50.0
    assert all(rule["firing"] for rule in alerts)


def test_tool_failure_is_counted() -> None:
    metrics.reset()
    STATE["tool_fail"] = True
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/chat",
                json={"user_id": "u1", "session_id": "s1", "feature": "qa", "message": "monitoring"},
            )
        assert response.status_code == 500
        assert metrics.snapshot()["error_breakdown"] == {"RuntimeError": 1}
    finally:
        STATE["tool_fail"] = False