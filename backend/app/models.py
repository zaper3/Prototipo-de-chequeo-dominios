from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ScanStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanProfile(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class RiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScanOptions(BaseModel):
    """Opciones heredadas de 0.1; se mantienen hasta estabilizar la API."""

    full_port_scan: bool = False
    active_subdomains: bool = True
    enrich_external: bool = True


class ScanRequest(BaseModel):
    target: str | None = Field(default=None, min_length=1, max_length=2048)
    domain: str | None = Field(default=None, min_length=1, max_length=2048)
    profile: ScanProfile | None = None
    authorized: Literal[True]
    deep_authorized: bool = False
    options: ScanOptions | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "ScanRequest":
        if not (self.target or self.domain):
            raise ValueError("Debes indicar target o domain.")
        if self.effective_profile == ScanProfile.DEEP and not self.deep_authorized:
            raise ValueError("El perfil profundo requiere confirmación adicional.")
        return self

    @property
    def requested_target(self) -> str:
        return (self.target or self.domain or "").strip()

    @property
    def effective_profile(self) -> ScanProfile:
        if self.profile is not None:
            return self.profile
        if self.options and self.options.full_port_scan:
            return ScanProfile.DEEP
        return ScanProfile.STANDARD


class FindingEvidence(BaseModel):
    key: str
    value: str


class Finding(BaseModel):
    id: str
    severity: Severity
    category: str
    title: str
    detail: str
    recommendation: str
    evidence: list[FindingEvidence] = Field(default_factory=list)
    source: str
    score_impact: int = Field(default=0, ge=0, le=100)
    reference: str | None = None


class CategoryScore(BaseModel):
    score: int = Field(ge=0, le=100)
    weight: int = Field(ge=0, le=100)
    available: bool = True
    checks: int = Field(default=0, ge=0)


class Coverage(BaseModel):
    completed_modules: list[str]
    expected_modules: list[str]
    missing_modules: list[str]
    percent: float = Field(ge=0, le=100)


class ScanReport(BaseModel):
    input_target: str
    domain: str
    profile: ScanProfile
    generated_at: datetime
    duration_seconds: float
    score: int = Field(ge=0, le=100)
    grade: str
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    coverage_percent: float = Field(ge=0, le=100)
    coverage: Coverage
    category_scores: dict[str, CategoryScore]
    ruleset_version: str
    summary: str
    top_actions: list[str]
    findings: list[Finding]
    ip_addresses: list[str]
    whois: dict[str, Any]
    domain_identity: dict[str, Any]
    dns: dict[str, list[str]]
    email_security: dict[str, Any]
    ssl: dict[str, Any]
    web_security: dict[str, Any]
    subdomains: list[dict[str, Any]]
    http: dict[str, Any]
    ports: list[dict[str, Any]]
    reputation: dict[str, Any]
    errors: dict[str, str]


class ScanJob(BaseModel):
    id: str
    input_target: str
    domain: str
    profile: ScanProfile
    status: ScanStatus
    stage: str = "En cola"
    progress: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    report: ScanReport | None = None
    error: str | None = None


class ScanHistoryItem(BaseModel):
    id: str
    input_target: str
    domain: str
    profile: ScanProfile
    status: ScanStatus
    created_at: datetime
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    score: int | None = None
    risk_level: RiskLevel | None = None
    confidence: ConfidenceLevel | None = None
    coverage_percent: float | None = None
    error: str | None = None


class ScanHistoryPage(BaseModel):
    items: list[ScanHistoryItem]
    total: int
    limit: int
    offset: int


class ScanChanges(BaseModel):
    scan_id: str
    previous_scan_id: str | None = None
    score_delta: int | None = None
    added_findings: list[str] = Field(default_factory=list)
    resolved_findings: list[str] = Field(default_factory=list)
    added_ports: list[int] = Field(default_factory=list)
    removed_ports: list[int] = Field(default_factory=list)
    added_subdomains: list[str] = Field(default_factory=list)
    removed_subdomains: list[str] = Field(default_factory=list)
    certificate_changed: bool = False


class DeleteAllRequest(BaseModel):
    confirm: Literal[True]


class DeleteResponse(BaseModel):
    deleted: int


class HealthResponse(BaseModel):
    status: str
    version: str
