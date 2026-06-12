from genai_hub.security.governance import DataGovernance


def test_pii_redaction_email():
    gov = DataGovernance(redaction_enabled=True)
    text = "Contact us at john.doe@example.com for details"
    redacted, fields = gov.redact_pii(text)
    assert "john.doe@example.com" not in redacted
    assert "email" in fields


def test_region_check():
    gov = DataGovernance(allowed_regions=["CH", "EU"])
    assert gov.check_region({"region": "CH"}) is True
    assert gov.check_region({"region": "US"}) is False
