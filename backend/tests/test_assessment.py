from app.models import RiskLevel, ScanProfile, Severity
from app.services.risk import assess_risk, classify_risk


def assess(**overrides):
    values = {
        "profile": ScanProfile.STANDARD,
        "identity": {"age_days": 365, "expiry_days": 180, "punycode": False},
        "dns_data": {
            "CAA": ["0 issue letsencrypt.org"],
            "MX": [],
            "TXT": [],
            "DS": ["key"],
        },
        "email_security": {"dnssec_present": True},
        "ssl_data": {"valid": True, "days_remaining": 90},
        "http_data": {"security_headers": {}},
        "web_security": {},
        "ports": [],
        "subdomains": [],
        "reputation": {
            "providers": {"virustotal": {"last_analysis_stats": {"malicious": 0}}}
        },
        "completed_modules": {
            "identity",
            "dns",
            "email",
            "tls",
            "http",
            "subdomains",
            "network",
            "reputation",
        },
        "expected_modules": [
            "identity",
            "dns",
            "email",
            "tls",
            "http",
            "subdomains",
            "network",
            "reputation",
        ],
    }
    values.update(overrides)
    return assess_risk(**values)


def test_assessment_returns_low_risk_for_complete_clean_evidence() -> None:
    score, _, risk, confidence, coverage, _, findings, _ = assess()
    assert score >= 85
    assert risk == RiskLevel.LOW
    assert confidence.value == "high"
    assert coverage.percent == 100
    assert findings == []


def test_confirmed_reputation_threat_forces_critical() -> None:
    result = assess(
        reputation={
            "providers": {"virustotal": {"last_analysis_stats": {"malicious": 2}}}
        }
    )
    assert result[2] == RiskLevel.CRITICAL
    assert any(item.severity == Severity.CRITICAL for item in result[6])


def test_missing_provider_lowers_confidence_not_score() -> None:
    with_provider = assess()
    without_provider = assess(
        reputation={"providers": {}},
        completed_modules={
            "identity",
            "dns",
            "email",
            "tls",
            "http",
            "subdomains",
            "network",
        },
    )
    assert without_provider[0] == with_provider[0]
    assert without_provider[3].value == "medium"
    assert without_provider[4].percent == 87.5


def test_coverage_below_half_returns_unknown() -> None:
    result = assess(completed_modules={"dns", "tls"})
    assert result[2] == RiskLevel.UNKNOWN


def test_risk_classification_score_boundaries() -> None:
    assert classify_risk(39, 100, set()) == RiskLevel.CRITICAL
    assert classify_risk(40, 100, set()) == RiskLevel.HIGH
    assert classify_risk(64, 100, set()) == RiskLevel.HIGH
    assert classify_risk(65, 100, set()) == RiskLevel.MODERATE
    assert classify_risk(84, 100, set()) == RiskLevel.MODERATE
    assert classify_risk(85, 100, set()) == RiskLevel.LOW


def test_finding_severity_can_raise_risk_category() -> None:
    assert classify_risk(95, 100, {Severity.MEDIUM}) == RiskLevel.MODERATE
    assert classify_risk(95, 100, {Severity.HIGH}) == RiskLevel.HIGH
    assert classify_risk(95, 100, {Severity.CRITICAL}) == RiskLevel.CRITICAL
    assert classify_risk(95, 49.9, {Severity.CRITICAL}) == RiskLevel.UNKNOWN
