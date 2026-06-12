import re
from dataclasses import dataclass, field
from typing import Any


PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone_ch": re.compile(r"\b(?:\+41|0)\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b"),
    "iban": re.compile(r"\bCH\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d\b"),
    "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
}


@dataclass
class GovernanceReport:
    redacted_fields: list[str] = field(default_factory=list)
    allowed_region: bool = True
    warnings: list[str] = field(default_factory=list)


class DataGovernance:
    """PII redaction and regional compliance checks before LLM calls."""

    def __init__(self, *, redaction_enabled: bool = True, allowed_regions: list[str] | None = None) -> None:
        self.redaction_enabled = redaction_enabled
        self.allowed_regions = allowed_regions or ["EU", "CH", "DE"]

    def redact_pii(self, text: str) -> tuple[str, list[str]]:
        if not self.redaction_enabled:
            return text, []

        redacted_fields: list[str] = []
        result = text
        for field_name, pattern in PII_PATTERNS.items():
            if pattern.search(result):
                redacted_fields.append(field_name)
                result = pattern.sub(f"[REDACTED_{field_name.upper()}]", result)
        return result, redacted_fields

    def check_region(self, record: dict[str, Any]) -> bool:
        region = record.get("region", "CH")
        return region in self.allowed_regions

    def prepare_for_llm(self, text: str, record: dict[str, Any] | None = None) -> tuple[str, GovernanceReport]:
        report = GovernanceReport()
        if record and not self.check_region(record):
            report.allowed_region = False
            report.warnings.append(f"Region '{record.get('region')}' outside allowed scope")

        redacted_text, fields = self.redact_pii(text)
        report.redacted_fields = fields
        return redacted_text, report
