// Reserved example names and TEST-NET addresses: no real target data.
const instant = "2026-10-31T10:06:00Z";
const findings = [
  {
    id: "DEMO-CSP", severity: "medium", category: "web_tls",
    title: "Content-Security-Policy no observada",
    detail: "Dato ficticio para mostrar cómo se presenta un hallazgo en el informe.",
    recommendation: "Revisar una política CSP adecuada para los recursos de la aplicación.",
    evidence: [{ key: "content-security-policy", value: "No incluida en el ejemplo" }],
    source: "Fixture documental HTTP", score_impact: 12,
    reference: "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP",
  },
  {
    id: "DEMO-DMARC", severity: "medium", category: "dns_email",
    title: "Política DMARC de observación",
    detail: "El ejemplo utiliza p=none para ilustrar una recomendación de correo.",
    recommendation: "Evaluar la política DMARC y revisar los informes antes de endurecerla.",
    evidence: [{ key: "_dmarc.example.test", value: "v=DMARC1; p=none" }],
    source: "Fixture documental DNS", score_impact: 8,
  },
];
export const report = {
  input_target: "https://example.test/ruta", domain: "example.test", profile: "standard",
  generated_at: instant, duration_seconds: 54.2, score: 78, grade: "B",
  risk_level: "moderate", confidence: "medium", coverage_percent: 87.5,
  coverage: {
    completed_modules: ["identity", "dns", "email", "tls", "http", "subdomains", "network"],
    expected_modules: ["identity", "dns", "email", "tls", "http", "subdomains", "network", "reputation"],
    missing_modules: ["reputation"],
    percent: 87.5,
  },
  category_scores: {
    reputation_identity: { score: 90, weight: 35, available: true, checks: 3 },
    web_tls: { score: 68, weight: 25, available: true, checks: 7 },
    dns_email: { score: 75, weight: 20, available: true, checks: 5 },
    network_exposure: { score: 72, weight: 20, available: true, checks: 4 },
  },
  ruleset_version: "2.0.0",
  summary: "Demostración con datos ficticios. La categoría ilustra señales observadas; no es una evaluación real ni garantiza que un sitio sea seguro.",
  top_actions: findings.map((finding) => finding.recommendation),
  findings, ip_addresses: ["192.0.2.10"],
  whois: { registrar: "Registrador de demostración", domain_name: "EXAMPLE.TEST" },
  domain_identity: { ascii_domain: "example.test", age_days: 900, expiry_days: 180, registrar: "Demostración" },
  dns: {
    A: ["192.0.2.10"], AAAA: [], MX: ["10 mail.example.test."],
    NS: ["ns1.example.test."], TXT: ['"v=spf1 -all"'], CAA: ['0 issue "example.test"'],
  },
  email_security: { spf: "v=spf1 -all", dmarc: "v=DMARC1; p=none", dnssec_present: true },
  ssl: { valid: true, version: "TLSv1.3", days_remaining: 80, issuer: "Emisor ficticio" },
  http: {
    url: "https://example.test/", status_code: 200,
    headers: { "strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff" },
    security_headers: {
      HSTS: { present: true, value: "max-age=31536000" },
      CSP: { present: false }, "X-Content-Type-Options": { present: true, value: "nosniff" },
    },
  },
  web_security: { wildcard_cors: false, insecure_cookies: 0, mixed_content: false },
  subdomains: ["www", "mail", "api", "status"].map((label) => ({
    name: label + ".example.test", sources: ["certificate-transparency"],
  })),
  ports: [
    { port: 80, protocol: "tcp", service: "http", risk: false },
    { port: 443, protocol: "tcp", service: "https", risk: false },
  ],
  reputation: { providers: {}, configured: [], errors: {} }, errors: {},
};
export const history = [
  { id: "docs-current", domain: "example.test", created_at: instant, score: 78, risk_level: "moderate" },
  { id: "docs-previous", domain: "example.test", created_at: "2026-10-30T09:00:00Z", score: 72, risk_level: "moderate" },
  { id: "docs-portal", domain: "portal.example.test", created_at: "2026-10-29T08:30:00Z", score: 55, risk_level: "high" },
].map((item) => ({
  ...item, input_target: "https://" + item.domain + "/ruta", profile: "standard",
  status: "completed", completed_at: item.created_at, duration_seconds: 54.2,
  confidence: "medium", coverage_percent: 87.5, error: null,
}));
export const job = {
  id: "docs-current", input_target: report.input_target, domain: report.domain,
  profile: report.profile, status: "completed", stage: "Informe completado", progress: 100,
  created_at: instant, updated_at: instant, completed_at: instant, report, error: null,
};
export const changes = {
  scan_id: "docs-current", previous_scan_id: "docs-previous", score_delta: 6,
  added_findings: [], resolved_findings: ["DEMO-OLD-TLS"], added_ports: [], removed_ports: [],
  added_subdomains: ["status.example.test"], removed_subdomains: [], certificate_changed: false,
};
