import pytest

from app.security import is_public_ip, normalize_domain, normalize_target


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Example.COM.", "example.com"),
        ("mañana.com", "xn--maana-pta.com"),
        ("https://Example.com/path?q=1", "example.com"),
    ],
)
def test_normalize_domain_or_url(raw: str, expected: str) -> None:
    assert normalize_domain(raw) == expected


def test_normalized_target_preserves_original_and_reports_url() -> None:
    target = normalize_target("https://example.com/a")
    assert target.original == "https://example.com/a"
    assert target.domain == "example.com"
    assert target.was_url is True


@pytest.mark.parametrize(
    "raw",
    [
        "example.com/path",
        "localhost",
        "127.0.0.1",
        "ftp://example.com/file",
        "https://user:pass@example.com",
        "https://example.com:8443",
    ],
)
def test_rejects_unsafe_or_ambiguous_targets(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_target(raw)


def test_only_globally_routable_ips_are_public() -> None:
    assert is_public_ip("8.8.8.8") is True
    assert is_public_ip("127.0.0.1") is False
    assert is_public_ip("10.0.0.1") is False
