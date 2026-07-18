import asyncio
import re
import socket
import ssl
import time
from datetime import date, datetime, timezone
from typing import Any, Awaitable, Callable, cast

import dns.asyncresolver
import httpx
import whois

from app.config import Settings
from app.models import ScanProfile, ScanReport
from app.security import normalize_target, resolve_public_ips
from app.services.risk import RULESET_VERSION, assess_risk


ProgressCallback = Callable[[str, int], Awaitable[None]]
COMMON_SUBDOMAINS = (
    "www",
    "mail",
    "api",
    "app",
    "dev",
    "staging",
    "test",
    "admin",
    "portal",
    "vpn",
    "remote",
    "blog",
    "shop",
    "support",
    "cdn",
    "static",
    "m",
    "ns1",
    "ns2",
)
SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
    "cross-origin-resource-policy": "Cross-Origin-Resource-Policy",
}
RISKY_PORTS = {
    21: "FTP",
    23: "Telnet",
    25: "SMTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    445: "SMB",
    1433: "MSSQL",
    1521: "Oracle",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    9200: "Elasticsearch",
    27017: "MongoDB",
}
STANDARD_EXTRA_PORTS = {
    1080,
    1433,
    1521,
    2049,
    2375,
    3000,
    3306,
    3389,
    5432,
    5601,
    5900,
    6379,
    8000,
    8080,
    8443,
    8888,
    9000,
    9200,
    27017,
}
EXPECTED_MODULES = {
    ScanProfile.QUICK: ["identity", "dns", "tls", "http", "reputation"],
    ScanProfile.STANDARD: [
        "identity",
        "dns",
        "email",
        "tls",
        "http",
        "subdomains",
        "network",
        "reputation",
    ],
    ScanProfile.DEEP: [
        "identity",
        "dns",
        "email",
        "tls",
        "tls_protocols",
        "http",
        "web_content",
        "subdomains",
        "network",
        "reputation",
    ],
}


def ports_for_profile(profile: ScanProfile) -> list[int]:
    if profile == ScanProfile.QUICK:
        return []
    if profile == ScanProfile.DEEP:
        return list(range(1, 65536))
    return sorted(set(range(1, 1025)) | STANDARD_EXTRA_PORTS)


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(_json_safe(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
            if item is not None
        }
    return value


async def _resolve_records(
    name: str, record_types: tuple[str, ...]
) -> dict[str, list[str]]:
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = 5
    result: dict[str, list[str]] = {}
    for record_type in record_types:
        try:
            answers = await resolver.resolve(
                name, record_type, raise_on_no_answer=False
            )
            result[record_type] = (
                sorted({answer.to_text() for answer in answers})
                if answers.rrset
                else []
            )
        except (dns.exception.DNSException, TimeoutError):
            result[record_type] = []
    return result


async def _dns_records(domain: str, profile: ScanProfile) -> dict[str, list[str]]:
    record_types = ("A", "AAAA", "MX", "NS", "TXT", "CAA", "SOA", "CNAME")
    if profile != ScanProfile.QUICK:
        record_types += ("DS", "DNSKEY")
    return await _resolve_records(domain, record_types)


async def _email_security(
    domain: str, dns_data: dict[str, list[str]]
) -> dict[str, Any]:
    dmarc, mta_sts, tls_rpt = await asyncio.gather(
        _resolve_records(f"_dmarc.{domain}", ("TXT",)),
        _resolve_records(f"_mta-sts.{domain}", ("TXT",)),
        _resolve_records(f"_smtp._tls.{domain}", ("TXT",)),
    )
    root_txt = " ".join(dns_data.get("TXT", []))
    return {
        "has_mx": bool(dns_data.get("MX")),
        "spf": next(
            (item for item in dns_data.get("TXT", []) if "v=spf1" in item.lower()), None
        ),
        "dmarc": next(
            (item for item in dmarc.get("TXT", []) if "v=dmarc1" in item.lower()), None
        ),
        "mta_sts": next(
            (item for item in mta_sts.get("TXT", []) if "v=stsv1" in item.lower()), None
        ),
        "tls_rpt": next(
            (item for item in tls_rpt.get("TXT", []) if "v=tlsrptv1" in item.lower()),
            None,
        ),
        "dnssec_present": bool(dns_data.get("DS") or dns_data.get("DNSKEY")),
        "root_txt_count": len(root_txt),
    }


async def _whois(domain: str) -> dict[str, Any]:
    data = await asyncio.to_thread(whois.whois, domain)
    return _json_safe(dict(data))


def _parse_date(value: Any) -> datetime | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _domain_identity(domain: str, whois_data: dict[str, Any]) -> dict[str, Any]:
    created = _parse_date(whois_data.get("creation_date"))
    expires = _parse_date(whois_data.get("expiration_date"))
    now = datetime.now(timezone.utc)
    return {
        "ascii_domain": domain,
        "unicode_domain": domain.encode("ascii").decode("idna")
        if "xn--" in domain
        else domain,
        "punycode": "xn--" in domain,
        "registrar": whois_data.get("registrar"),
        "creation_date": created.isoformat() if created else None,
        "expiration_date": expires.isoformat() if expires else None,
        "age_days": max(0, (now - created).days) if created else None,
        "expiry_days": (expires - now).days if expires else None,
        "country": whois_data.get("country"),
        "name_servers": whois_data.get("name_servers", []),
    }


def _tls_protocol_support(domain: str, ip: str) -> dict[str, bool]:
    versions = {
        "TLSv1": ssl.TLSVersion.TLSv1,
        "TLSv1.1": ssl.TLSVersion.TLSv1_1,
        "TLSv1.2": ssl.TLSVersion.TLSv1_2,
        "TLSv1.3": ssl.TLSVersion.TLSv1_3,
    }
    support: dict[str, bool] = {}
    for label, version in versions.items():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = version
        context.maximum_version = version
        try:
            with socket.create_connection((ip, 443), timeout=3) as raw_socket:
                with context.wrap_socket(raw_socket, server_hostname=domain):
                    support[label] = True
        except (OSError, ssl.SSLError):
            support[label] = False
    return support


def _ssl_sync(domain: str, ip: str, deep: bool) -> dict[str, Any]:
    context = ssl.create_default_context()
    with socket.create_connection((ip, 443), timeout=7) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=domain) as tls_socket:
            certificate = cast(dict[str, Any], tls_socket.getpeercert() or {})
            issuer = {
                key: value
                for group in certificate.get("issuer", ())
                for key, value in group
            }
            subject = {
                key: value
                for group in certificate.get("subject", ())
                for key, value in group
            }
            not_after = certificate.get("notAfter")
            expires_at = (
                datetime.strptime(str(not_after), "%b %d %H:%M:%S %Y %Z").replace(
                    tzinfo=timezone.utc
                )
                if not_after
                else None
            )
            cipher = tls_socket.cipher()
            result = {
                "valid": True,
                "subject": subject,
                "issuer": issuer,
                "serial_number": certificate.get("serialNumber"),
                "version": tls_socket.version(),
                "cipher": cipher[0] if cipher else None,
                "not_before": certificate.get("notBefore"),
                "not_after": not_after,
                "days_remaining": (expires_at - datetime.now(timezone.utc)).days
                if expires_at
                else None,
                "subject_alt_names": [
                    value
                    for kind, value in certificate.get("subjectAltName", ())
                    if kind == "DNS"
                ],
            }
    if deep:
        result["protocol_support"] = _tls_protocol_support(domain, ip)
    return result


async def _ssl_info(domain: str, ip: str, deep: bool) -> dict[str, Any]:
    return await asyncio.to_thread(_ssl_sync, domain, ip, deep)


async def _read_response(
    client: httpx.AsyncClient, url: str, limit: int = 1_000_000
) -> dict[str, Any]:
    async with client.stream("GET", url, follow_redirects=False) as response:
        content = bytearray()
        async for chunk in response.aiter_bytes():
            content.extend(chunk[: max(0, limit - len(content))])
            if len(content) >= limit:
                break
        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "reason": response.reason_phrase,
            "headers": {key.lower(): value for key, value in response.headers.items()},
            "set_cookies": response.headers.get_list("set-cookie"),
            "body": bytes(content).decode(
                response.encoding or "utf-8", errors="replace"
            ),
        }


async def _http_info(domain: str, deep: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    async with httpx.AsyncClient(
        timeout=10,
        verify=True,
        headers={"User-Agent": "DomainCheckPrototype/0.2"},
    ) as client:
        responses: dict[str, dict[str, Any]] = {}
        errors: dict[str, str] = {}
        for scheme in ("https", "http"):
            try:
                responses[scheme] = await _read_response(
                    client, f"{scheme}://{domain}/"
                )
            except httpx.HTTPError as exc:
                errors[scheme] = str(exc)
        primary = responses.get("https") or responses.get("http")
        if not primary:
            raise RuntimeError(
                "; ".join(errors.values())
                or "No fue posible conectar por HTTP o HTTPS."
            )

        headers = primary["headers"]
        cookies = primary.get("set_cookies", [])
        insecure_cookies = [
            cookie
            for cookie in cookies
            if "secure" not in cookie.lower()
            or "httponly" not in cookie.lower()
            or "samesite" not in cookie.lower()
        ]
        http_location = responses.get("http", {}).get("headers", {}).get("location")
        body = primary.pop("body", "")
        primary.update(
            {
                "redirect_to": headers.get("location"),
                "http_status_code": responses.get("http", {}).get("status_code"),
                "http_redirect_to": http_location,
                "redirects_http_to_https": bool(
                    http_location and http_location.lower().startswith("https://")
                ),
                "security_headers": {
                    label: {"present": name in headers, "value": headers.get(name)}
                    for name, label in SECURITY_HEADERS.items()
                },
                "server": headers.get("server"),
                "powered_by": headers.get("x-powered-by"),
                "body_truncated_at": 1_000_000 if len(body) >= 1_000_000 else None,
            }
        )
        web_security = {
            "wildcard_cors": headers.get("access-control-allow-origin") == "*",
            "insecure_cookies": len(insecure_cookies),
            "cookie_count": len(cookies),
            "mixed_content": bool(
                deep
                and primary["url"].startswith("https://")
                and re.search(r"(?:src|href)=[\"']http://", body, re.I)
            ),
            "password_form_over_http": bool(
                primary["url"].startswith("http://")
                and re.search(r"type=[\"']password", body, re.I)
            ),
            "security_txt": False,
        }
        if deep:
            try:
                security_txt = await client.get(
                    f"https://{domain}/.well-known/security.txt",
                    follow_redirects=False,
                )
                web_security["security_txt"] = security_txt.status_code == 200
            except httpx.HTTPError:
                pass
        return primary, web_security


async def _ct_subdomains(domain: str, client: httpx.AsyncClient) -> set[str]:
    response = await client.get(
        "https://crt.sh/", params={"q": f"%.{domain}", "output": "json"}
    )
    response.raise_for_status()
    names: set[str] = set()
    for row in response.json():
        for name in row.get("name_value", "").splitlines():
            clean = name.strip().lower().removeprefix("*.").rstrip(".")
            if clean == domain or clean.endswith(f".{domain}"):
                names.add(clean)
    return names


async def _active_subdomains(domain: str) -> set[str]:
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = 2

    async def check(label: str) -> str | None:
        candidate = f"{label}.{domain}"
        try:
            await resolver.resolve(candidate, "A")
            return candidate
        except dns.exception.DNSException:
            return None

    values = await asyncio.gather(*(check(label) for label in COMMON_SUBDOMAINS))
    return {value for value in values if value}


async def _inspect_subdomain(name: str) -> dict[str, Any]:
    records = await _resolve_records(name, ("A", "AAAA", "CNAME"))
    cname = records.get("CNAME", [])
    potential_dangling = False
    if cname:
        target = cname[0].rstrip(".")
        target_records = await _resolve_records(target, ("A", "AAAA"))
        potential_dangling = not bool(
            target_records.get("A") or target_records.get("AAAA")
        )
    return {
        "ip_addresses": records.get("A", []) + records.get("AAAA", []),
        "cname": cname,
        "potential_dangling": potential_dangling,
    }


async def _subdomains(
    domain: str,
    profile: ScanProfile,
    client: httpx.AsyncClient,
    limit: int,
) -> list[dict[str, Any]]:
    passive = await _ct_subdomains(domain, client)
    active_names = (
        await _active_subdomains(domain) if profile == ScanProfile.DEEP else set()
    )
    all_names = sorted(passive | active_names)[: max(1, limit)]
    details = (
        await asyncio.gather(*(_inspect_subdomain(name) for name in all_names))
        if profile == ScanProfile.DEEP
        else [{} for _ in all_names]
    )
    return [
        {
            "name": name,
            "sources": [
                source
                for source, names in (
                    ("certificate-transparency", passive),
                    ("active-dns", active_names),
                )
                if name in names
            ],
            **detail,
        }
        for name, detail in zip(all_names, details, strict=True)
    ]


def _service_name(port: int) -> str:
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return RISKY_PORTS.get(port, "desconocido")


async def _grab_banner(ip: str, domain: str, port: int, timeout: float) -> str | None:
    writer = None
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        if port in {80, 8000, 8080, 8888, 9000}:
            writer.write(f"HEAD / HTTP/1.0\r\nHost: {domain}\r\n\r\n".encode())
            await writer.drain()
        data = await asyncio.wait_for(reader.read(256), timeout=max(0.5, timeout))
        clean = " ".join(data.decode("utf-8", errors="replace").split())
        return clean[:240] or None
    except (asyncio.TimeoutError, ConnectionError, OSError):
        return None
    finally:
        if writer:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass


async def _scan_ports(
    ip: str,
    domain: str,
    ports: list[int],
    settings: Settings,
    banners: bool,
) -> list[dict[str, Any]]:
    queue: asyncio.Queue[int] = asyncio.Queue()
    for port in ports:
        queue.put_nowait(port)
    open_ports: list[int] = []
    deadline = time.monotonic() + settings.scan_max_seconds

    async def worker() -> None:
        while not queue.empty() and time.monotonic() < deadline:
            try:
                port = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            writer = None
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=settings.port_scan_timeout_seconds,
                )
                open_ports.append(port)
            except (asyncio.TimeoutError, ConnectionError, OSError):
                pass
            finally:
                if writer:
                    writer.close()
                    try:
                        await writer.wait_closed()
                    except OSError:
                        pass
                queue.task_done()

    worker_count = max(1, min(settings.port_scan_concurrency, 500))
    await asyncio.gather(*(worker() for _ in range(worker_count)))
    banner_values = (
        await asyncio.gather(
            *(
                _grab_banner(ip, domain, port, settings.port_scan_timeout_seconds)
                for port in sorted(open_ports)
            )
        )
        if banners
        else [None] * len(open_ports)
    )
    return [
        {
            "port": port,
            "protocol": "tcp",
            "service": _service_name(port),
            "risk": port in RISKY_PORTS,
            "banner": banner,
        }
        for port, banner in zip(sorted(open_ports), banner_values, strict=True)
    ]


async def _reputation(
    domain: str, settings: Settings, client: httpx.AsyncClient
) -> dict[str, Any]:
    result: dict[str, Any] = {"providers": {}, "configured": [], "errors": {}}

    async def provider(name: str, operation: Awaitable[dict[str, Any]]) -> None:
        result["configured"].append(name)
        try:
            result["providers"][name] = await operation
        except Exception as exc:
            result["errors"][name] = str(exc)

    async def virustotal() -> dict[str, Any]:
        response = await client.get(
            f"https://www.virustotal.com/api/v3/domains/{domain}",
            headers={"x-apikey": settings.virustotal_api_key or ""},
        )
        response.raise_for_status()
        attributes = response.json().get("data", {}).get("attributes", {})
        return {
            "last_analysis_stats": attributes.get("last_analysis_stats", {}),
            "reputation": attributes.get("reputation"),
            "categories": attributes.get("categories", {}),
        }

    async def securitytrails() -> dict[str, Any]:
        response = await client.get(
            f"https://api.securitytrails.com/v1/domain/{domain}/subdomains",
            headers={"APIKEY": settings.securitytrails_api_key or ""},
        )
        response.raise_for_status()
        return {"subdomains": response.json().get("subdomains", [])}

    async def safe_browsing() -> dict[str, Any]:
        response = await client.get(
            "https://safebrowsing.googleapis.com/v5/urls:search",
            params={
                "urls": f"https://{domain}/",
                "key": settings.google_safe_browsing_api_key or "",
            },
        )
        response.raise_for_status()
        return response.json()

    async def observatory() -> dict[str, Any]:
        response = await client.post(
            "https://observatory-api.mdn.mozilla.net/api/v2/scan",
            params={"host": domain},
        )
        response.raise_for_status()
        return response.json()

    operations = []
    if settings.virustotal_api_key:
        operations.append(provider("virustotal", virustotal()))
    if settings.securitytrails_api_key:
        operations.append(provider("securitytrails", securitytrails()))
    if settings.google_safe_browsing_api_key:
        operations.append(provider("google_safe_browsing", safe_browsing()))
    if settings.mdn_observatory_enabled:
        operations.append(provider("mdn_observatory", observatory()))
    if operations:
        await asyncio.gather(*operations)
    return result


async def run_scan(
    raw_target: str,
    profile: ScanProfile,
    settings: Settings,
    progress: ProgressCallback,
) -> ScanReport:
    started = time.monotonic()
    target = normalize_target(raw_target)
    domain = target.domain
    errors: dict[str, str] = {}
    completed_modules: set[str] = set()

    await progress("Validando objetivo y resolviendo IP", 5)
    ip_addresses = await resolve_public_ips(domain)

    async def collect(name: str, task: asyncio.Task[Any], fallback: Any) -> Any:
        try:
            value = await task
            completed_modules.add(name)
            return value
        except Exception as exc:
            errors[name] = str(exc)
            return fallback

    await progress("Consultando identidad, DNS, TLS y web", 15)
    dns_task = asyncio.create_task(_dns_records(domain, profile))
    whois_task = asyncio.create_task(_whois(domain))
    ssl_task = asyncio.create_task(
        _ssl_info(domain, ip_addresses[0], profile == ScanProfile.DEEP)
    )
    http_task = asyncio.create_task(_http_info(domain, profile == ScanProfile.DEEP))

    async with httpx.AsyncClient(
        timeout=20, headers={"User-Agent": "DomainCheckPrototype/0.2"}
    ) as client:
        reputation_task = asyncio.create_task(_reputation(domain, settings, client))
        subdomain_task = (
            asyncio.create_task(
                _subdomains(domain, profile, client, settings.subdomain_result_limit)
            )
            if profile != ScanProfile.QUICK
            else None
        )

        dns_data = await collect("dns", dns_task, {})
        whois_data = await collect("identity", whois_task, {})
        identity = _domain_identity(domain, whois_data)
        email_security = {}
        if profile != ScanProfile.QUICK:
            try:
                email_security = await _email_security(domain, dns_data)
                completed_modules.add("email")
            except Exception as exc:
                errors["email"] = str(exc)

        await progress("Analizando TLS, HTTP y reputación", 38)
        ssl_data = await collect("tls", ssl_task, {"valid": False})
        if profile == ScanProfile.DEEP and "protocol_support" in ssl_data:
            completed_modules.add("tls_protocols")
        http_pair = await collect("http", http_task, ({}, {}))
        http_data, web_security = http_pair
        if profile == ScanProfile.DEEP and http_data:
            completed_modules.add("web_content")
        reputation = await collect(
            "reputation_request",
            reputation_task,
            {"providers": {}, "configured": [], "errors": {}},
        )
        if reputation.get("providers"):
            completed_modules.add("reputation")
        subdomains = (
            await collect("subdomains", subdomain_task, []) if subdomain_task else []
        )

    ports: list[dict[str, Any]] = []
    if profile != ScanProfile.QUICK:
        deep = profile == ScanProfile.DEEP
        port_numbers = ports_for_profile(profile)
        await progress(
            "Escaneando puertos TCP 1–65535"
            if deep
            else "Comprobando puertos TCP frecuentes",
            58,
        )
        try:
            ports = await _scan_ports(
                ip_addresses[0],
                domain,
                port_numbers,
                settings,
                banners=deep,
            )
            completed_modules.add("network")
        except Exception as exc:
            errors["network"] = str(exc)

    await progress("Calculando riesgo, cobertura y acciones", 92)
    (
        score,
        grade,
        risk_level,
        confidence,
        coverage,
        category_scores,
        findings,
        top_actions,
    ) = assess_risk(
        profile=profile,
        identity=identity,
        dns_data=dns_data,
        email_security=email_security,
        ssl_data=ssl_data,
        http_data=http_data,
        web_security=web_security,
        ports=ports,
        subdomains=subdomains,
        reputation=reputation,
        completed_modules=completed_modules,
        expected_modules=EXPECTED_MODULES[profile],
    )
    risk_labels = {
        "low": "riesgo observado bajo",
        "moderate": "riesgo observado moderado",
        "high": "riesgo observado alto",
        "critical": "riesgo observado crítico",
        "unknown": "datos insuficientes",
    }
    summary = (
        f"El análisis clasifica el dominio con {risk_labels[risk_level.value]} "
        f"({score}/100, confianza {confidence.value}, cobertura {coverage.percent:.0f}%). "
        "La categoría describe señales observadas y no garantiza que el sitio sea seguro."
    )
    await progress("Informe completado", 100)
    return ScanReport(
        input_target=target.original,
        domain=domain,
        profile=profile,
        generated_at=datetime.now(timezone.utc),
        duration_seconds=round(time.monotonic() - started, 2),
        score=score,
        grade=grade,
        risk_level=risk_level,
        confidence=confidence,
        coverage_percent=coverage.percent,
        coverage=coverage,
        category_scores=category_scores,
        ruleset_version=RULESET_VERSION,
        summary=summary,
        top_actions=top_actions,
        findings=findings,
        ip_addresses=ip_addresses,
        whois=whois_data,
        domain_identity=identity,
        dns=dns_data,
        email_security=email_security,
        ssl=ssl_data,
        web_security=web_security,
        subdomains=subdomains,
        http=http_data,
        ports=ports,
        reputation=reputation,
        errors=errors,
    )
