from app.models import ScanProfile
from app.services.scanner import EXPECTED_MODULES, ports_for_profile


def test_quick_profile_has_no_active_network_or_subdomain_modules() -> None:
    assert ports_for_profile(ScanProfile.QUICK) == []
    assert "network" not in EXPECTED_MODULES[ScanProfile.QUICK]
    assert "subdomains" not in EXPECTED_MODULES[ScanProfile.QUICK]


def test_standard_profile_limits_network_scope() -> None:
    ports = ports_for_profile(ScanProfile.STANDARD)
    assert ports[:3] == [1, 2, 3]
    assert 1024 in ports
    assert 3389 in ports
    assert 65535 not in ports
    assert "web_content" not in EXPECTED_MODULES[ScanProfile.STANDARD]


def test_deep_profile_enables_full_tcp_and_expanded_modules() -> None:
    ports = ports_for_profile(ScanProfile.DEEP)
    assert len(ports) == 65535
    assert ports[0] == 1
    assert ports[-1] == 65535
    assert {"network", "tls_protocols", "web_content", "subdomains"} <= set(
        EXPECTED_MODULES[ScanProfile.DEEP]
    )
