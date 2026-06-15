from app.metrics import percentile, record_error, record_request, reset, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100

def test_snapshot_aggregates_success_and_error() -> None:
    reset()
    record_request(100, 0.001, 20, 80, 0.8)
    record_error("RuntimeError")
    result = snapshot()
    assert result["traffic"] == 2
    assert result["error_rate_pct"] == 50.0
    assert result["tokens_out_total"] == 80