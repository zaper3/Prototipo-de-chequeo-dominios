from typing import Any

from app.models import (
    CategoryScore,
    ConfidenceLevel,
    Coverage,
    Finding,
    FindingEvidence,
    RiskLevel,
    ScanProfile,
    Severity,
)


RULESET_VERSION = "2.0.0"
CATEGORY_WEIGHTS = {
    "reputation_identity": 35,
    "web_tls": 25,
    "dns_email": 20,
    "network_exposure": 20,
}


def classify_risk(
    score: int, coverage_percent: float, severities: set[Severity]
) -> RiskLevel:
    if coverage_percent < 50:
        return RiskLevel.UNKNOWN
    if Severity.CRITICAL in severities or score < 40:
        return RiskLevel.CRITICAL
    if Severity.HIGH in severities or score < 65:
        return RiskLevel.HIGH
    if Severity.MEDIUM in severities or score < 85:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def _finding(
    finding_id: str,
    severity: Severity,
    category: str,
    title: str,
    detail: str,
    recommendation: str,
    source: str,
    impact: int,
    *,
    evidence: dict[str, Any] | None = None,
    reference: str | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        severity=severity,
        category=category,
        title=title,
        detail=detail,
        recommendation=recommendation,
        evidence=[
            FindingEvidence(key=key, value=str(value))
            for key, value in (evidence or {}).items()
        ],
        source=source,
        score_impact=impact,
        reference=reference,
    )


def assess_risk(
    *,
    profile: ScanProfile,
    identity: dict[str, Any],
    dns_data: dict[str, list[str]],
    email_security: dict[str, Any],
    ssl_data: dict[str, Any],
    http_data: dict[str, Any],
    web_security: dict[str, Any],
    ports: list[dict[str, Any]],
    subdomains: list[dict[str, Any]],
    reputation: dict[str, Any],
    completed_modules: set[str],
    expected_modules: list[str],
) -> tuple[
    int,
    str,
    RiskLevel,
    ConfidenceLevel,
    Coverage,
    dict[str, CategoryScore],
    list[Finding],
    list[str],
]:
    penalties = {category: 0 for category in CATEGORY_WEIGHTS}
    checks = {category: 0 for category in CATEGORY_WEIGHTS}
    findings: list[Finding] = []

    def add(item: Finding) -> None:
        findings.append(item)
        penalties[item.category] = min(
            100, penalties[item.category] + item.score_impact
        )
        checks[item.category] += 1

    vt_stats = (
        reputation.get("providers", {})
        .get("virustotal", {})
        .get("last_analysis_stats", {})
    )
    malicious = int(vt_stats.get("malicious", 0) or 0)
    if malicious:
        add(
            _finding(
                "REP-VT-MALICIOUS",
                Severity.CRITICAL,
                "reputation_identity",
                "Detecciones maliciosas confirmadas",
                f"VirusTotal informa {malicious} motores con resultado malicioso.",
                "Investigar los indicadores y evitar el acceso hasta completar la validación.",
                "VirusTotal",
                70,
                evidence={"malicious": malicious},
                reference="https://docs.virustotal.com/reference/domains",
            )
        )
    safe_browsing = reputation.get("providers", {}).get("google_safe_browsing", {})
    threats = safe_browsing.get("threats", [])
    if threats:
        add(
            _finding(
                "REP-GSB-THREAT",
                Severity.CRITICAL,
                "reputation_identity",
                "URL incluida en listas de amenazas",
                "Google Safe Browsing devolvió coincidencias para el dominio.",
                "No visitar ni introducir credenciales hasta investigar las coincidencias.",
                "Google Safe Browsing",
                100,
                evidence={"matches": len(threats)},
                reference="https://developers.google.com/safe-browsing/reference/rest",
            )
        )

    age_days = identity.get("age_days")
    if isinstance(age_days, int) and age_days < 30:
        add(
            _finding(
                "IDENTITY-NEW-DOMAIN",
                Severity.MEDIUM,
                "reputation_identity",
                "Dominio registrado recientemente",
                f"La antigüedad observada es de {age_days} días.",
                "Validar propietario, propósito y reputación antes de confiar información sensible.",
                "WHOIS/RDAP",
                15,
                evidence={"age_days": age_days},
            )
        )
    expiry_days = identity.get("expiry_days")
    if isinstance(expiry_days, int) and expiry_days < 30:
        add(
            _finding(
                "IDENTITY-EXPIRING",
                Severity.LOW,
                "reputation_identity",
                "Registro próximo a caducar",
                f"El registro podría caducar en {expiry_days} días.",
                "Renovar el dominio y verificar la renovación automática.",
                "WHOIS/RDAP",
                5,
                evidence={"expiry_days": expiry_days},
            )
        )
    if identity.get("punycode"):
        add(
            _finding(
                "IDENTITY-IDN",
                Severity.LOW,
                "reputation_identity",
                "Dominio internacionalizado",
                "El dominio utiliza representación Punycode; por sí sola no implica actividad maliciosa.",
                "Verificar visualmente el nombre para descartar caracteres similares o suplantación.",
                "IDNA",
                5,
                evidence={"ascii_domain": identity.get("ascii_domain", "")},
            )
        )

    if not ssl_data.get("valid"):
        add(
            _finding(
                "TLS-INVALID",
                Severity.HIGH,
                "web_tls",
                "HTTPS sin certificado válido",
                "No se pudo validar un certificado TLS para el dominio.",
                "Instalar un certificado válido y revisar la cadena de confianza.",
                "TLS",
                40,
                reference="https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html",
            )
        )
    elif (
        isinstance(ssl_data.get("days_remaining"), int)
        and ssl_data["days_remaining"] < 30
    ):
        add(
            _finding(
                "TLS-EXPIRING",
                Severity.MEDIUM,
                "web_tls",
                "Certificado próximo a caducar",
                f"Quedan {ssl_data['days_remaining']} días de validez.",
                "Renovar el certificado antes de su caducidad.",
                "TLS",
                15,
                evidence={"days_remaining": ssl_data["days_remaining"]},
            )
        )
    weak_protocols = [
        protocol
        for protocol, supported in ssl_data.get("protocol_support", {}).items()
        if protocol in {"TLSv1", "TLSv1.1"} and supported
    ]
    if weak_protocols:
        add(
            _finding(
                "TLS-WEAK-PROTOCOL",
                Severity.HIGH,
                "web_tls",
                "Protocolos TLS obsoletos admitidos",
                f"El servidor acepta: {', '.join(weak_protocols)}.",
                "Deshabilitar TLS 1.0/1.1 y exigir TLS 1.2 o superior.",
                "TLS",
                25,
                evidence={"protocols": ", ".join(weak_protocols)},
            )
        )

    security_headers = http_data.get("security_headers", {})
    missing_headers = [
        name for name, state in security_headers.items() if not state.get("present")
    ]
    if missing_headers:
        add(
            _finding(
                "HTTP-MISSING-HEADERS",
                Severity.MEDIUM,
                "web_tls",
                "Cabeceras defensivas incompletas",
                f"No se encontraron: {', '.join(missing_headers)}.",
                "Aplicar una política de cabeceras adaptada al sitio siguiendo OWASP/MDN.",
                "HTTP",
                min(20, len(missing_headers) * 3),
                evidence={"missing": ", ".join(missing_headers)},
                reference="https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html",
            )
        )
    if web_security.get("wildcard_cors"):
        add(
            _finding(
                "HTTP-CORS-WILDCARD",
                Severity.LOW,
                "web_tls",
                "CORS permite cualquier origen",
                "La respuesta incluye Access-Control-Allow-Origin: *.",
                "Comprobar si el recurso debe ser público y restringir orígenes cuando corresponda.",
                "HTTP",
                5,
            )
        )
    if web_security.get("insecure_cookies"):
        add(
            _finding(
                "HTTP-INSECURE-COOKIE",
                Severity.MEDIUM,
                "web_tls",
                "Cookies sin atributos defensivos",
                "Se observaron cookies sin Secure, HttpOnly o SameSite.",
                "Aplicar atributos seguros según el uso de cada cookie.",
                "HTTP",
                10,
            )
        )
    if web_security.get("mixed_content"):
        add(
            _finding(
                "HTTP-MIXED-CONTENT",
                Severity.MEDIUM,
                "web_tls",
                "Contenido mixto potencial",
                "La portada HTTPS referencia recursos mediante HTTP.",
                "Servir todos los recursos mediante HTTPS y actualizar referencias absolutas.",
                "HTML",
                10,
            )
        )
    if web_security.get("password_form_over_http"):
        add(
            _finding(
                "HTTP-PASSWORD-INSECURE",
                Severity.CRITICAL,
                "web_tls",
                "Formulario de contraseña servido por HTTP",
                "Se detectó un campo de contraseña en una página sin HTTPS.",
                "Bloquear el formulario y redirigir todo el sitio a HTTPS inmediatamente.",
                "HTML",
                60,
            )
        )

    has_mail = bool(dns_data.get("MX"))
    if not dns_data.get("CAA"):
        add(
            _finding(
                "DNS-NO-CAA",
                Severity.LOW,
                "dns_email",
                "Registro CAA ausente",
                "DNS no limita qué autoridades pueden emitir certificados.",
                "Publicar un registro CAA acorde con la autoridad utilizada.",
                "DNS",
                5,
            )
        )
    if not email_security.get("dnssec_present"):
        add(
            _finding(
                "DNS-NO-DNSSEC",
                Severity.LOW,
                "dns_email",
                "DNSSEC no detectado",
                "No se observaron registros DS/DNSKEY en la consulta básica.",
                "Evaluar la firma DNSSEC con el registrador y proveedor DNS.",
                "DNS",
                5,
            )
        )
    if has_mail and not email_security.get("spf"):
        add(
            _finding(
                "MAIL-NO-SPF",
                Severity.MEDIUM,
                "dns_email",
                "SPF no detectado",
                "El dominio publica MX pero no una política SPF visible.",
                "Publicar una política SPF que autorice únicamente remitentes legítimos.",
                "DNS/TXT",
                8,
            )
        )
    if has_mail and not email_security.get("dmarc"):
        add(
            _finding(
                "MAIL-NO-DMARC",
                Severity.MEDIUM,
                "dns_email",
                "DMARC no detectado",
                "No se encontró política DMARC para un dominio con servicio de correo.",
                "Publicar DMARC, iniciar con monitorización y avanzar hacia quarantine/reject.",
                "DNS/TXT",
                12,
            )
        )

    risky_ports = [port for port in ports if port.get("risk")]
    if risky_ports:
        add(
            _finding(
                "NET-SENSITIVE-PORTS",
                Severity.HIGH,
                "network_exposure",
                "Servicios sensibles expuestos",
                "Puertos de especial atención: "
                + ", ".join(str(item["port"]) for item in risky_ports)
                + ".",
                "Confirmar la necesidad de exposición y aplicar filtrado, autenticación y parcheo.",
                "TCP",
                min(35, 6 * len(risky_ports)),
                evidence={
                    "ports": ", ".join(str(item["port"]) for item in risky_ports)
                },
            )
        )
    dangling = [item["name"] for item in subdomains if item.get("potential_dangling")]
    if dangling:
        add(
            _finding(
                "DNS-DANGLING-CNAME",
                Severity.HIGH,
                "network_exposure",
                "CNAME potencialmente colgante",
                f"Se observaron {len(dangling)} candidatos que requieren validación manual.",
                "Eliminar el CNAME o reclamar el recurso externo; no intentar tomar control durante el análisis.",
                "DNS",
                25,
                evidence={"subdomains": ", ".join(dangling[:10])},
            )
        )

    available = {
        "reputation_identity": bool({"identity", "reputation"} & completed_modules),
        "web_tls": bool({"tls", "http"} & completed_modules),
        "dns_email": "dns" in completed_modules,
        "network_exposure": profile != ScanProfile.QUICK
        and "network" in completed_modules,
    }
    category_scores = {
        category: CategoryScore(
            score=max(0, 100 - penalties[category]),
            weight=weight,
            available=available[category],
            checks=checks[category],
        )
        for category, weight in CATEGORY_WEIGHTS.items()
    }
    available_weight = sum(
        item.weight for item in category_scores.values() if item.available
    )
    score = round(
        sum(
            item.score * item.weight
            for item in category_scores.values()
            if item.available
        )
        / max(1, available_weight)
    )

    expected = list(dict.fromkeys(expected_modules))
    completed = sorted(set(expected) & completed_modules)
    missing = sorted(set(expected) - completed_modules)
    coverage_percent = round(len(completed) * 100 / max(1, len(expected)), 1)
    coverage = Coverage(
        completed_modules=completed,
        expected_modules=expected,
        missing_modules=missing,
        percent=coverage_percent,
    )
    providers = reputation.get("providers", {})
    confidence = (
        ConfidenceLevel.HIGH
        if coverage_percent >= 85 and providers
        else ConfidenceLevel.MEDIUM
        if coverage_percent >= 60
        else ConfidenceLevel.LOW
    )

    severities = {finding.severity for finding in findings}
    risk_level = classify_risk(score, coverage_percent, severities)

    grade = (
        "A"
        if score >= 90
        else "B"
        if score >= 75
        else "C"
        if score >= 60
        else "D"
        if score >= 40
        else "F"
    )
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }
    findings.sort(
        key=lambda item: (severity_order[item.severity], -item.score_impact, item.id)
    )
    top_actions = list(dict.fromkeys(item.recommendation for item in findings))[:3]
    return (
        score,
        grade,
        risk_level,
        confidence,
        coverage,
        category_scores,
        findings,
        top_actions,
    )
