from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out

def test_scrub_all_supported_pii() -> None:
    out = scrub_text(
        "Phone 0987654321, CCCD 001234567890, card 4111 1111 1111 1111, "
        "passport B1234567, IP 192.168.1.10, address: 10 Main Street"
    )
    for leaked in ["0987654321", "001234567890", "4111", "B1234567", "192.168.1.10", "10 Main Street"]:
        assert leaked not in out