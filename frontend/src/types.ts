export type ScanStatus = "queued" | "running" | "completed" | "failed" | "interrupted";
export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type ScanProfile = "quick" | "standard" | "deep";
export type RiskLevel = "low" | "moderate" | "high" | "critical" | "unknown";
export type ConfidenceLevel = "high" | "medium" | "low";

export interface Finding {
  id: string;
  severity: Severity;
  category: string;
  title: string;
  detail: string;
  recommendation: string;
  evidence: Array<{ key: string; value: string }>;
  source: string;
  score_impact: number;
  reference?: string;
}

export interface CategoryScore {
  score: number;
  weight: number;
  available: boolean;
  checks: number;
}

export interface Coverage {
  completed_modules: string[];
  expected_modules: string[];
  missing_modules: string[];
  percent: number;
}

export interface ScanReport {
  input_target: string;
  domain: string;
  profile: ScanProfile;
  generated_at: string;
  duration_seconds: number;
  score: number;
  grade: string;
  risk_level: RiskLevel;
  confidence: ConfidenceLevel;
  coverage_percent: number;
  coverage: Coverage;
  category_scores: Record<string, CategoryScore>;
  ruleset_version: string;
  summary: string;
  top_actions: string[];
  findings: Finding[];
  ip_addresses: string[];
  whois: Record<string, unknown>;
  domain_identity: Record<string, unknown>;
  dns: Record<string, string[]>;
  email_security: Record<string, unknown>;
  ssl: Record<string, unknown>;
  web_security: Record<string, unknown>;
  subdomains: Array<{
    name: string;
    sources: string[];
    ip_addresses?: string[];
    cname?: string[];
    potential_dangling?: boolean;
  }>;
  http: {
    url?: string;
    status_code?: number;
    reason?: string;
    headers?: Record<string, string>;
    redirect_to?: string;
    security_headers?: Record<string, { present: boolean; value?: string }>;
    server?: string;
    powered_by?: string;
  };
  ports: Array<{ port: number; protocol: string; service: string; risk: boolean; banner?: string }>;
  reputation: Record<string, unknown>;
  errors: Record<string, string>;
}

export interface ScanJob {
  id: string;
  input_target: string;
  domain: string;
  profile: ScanProfile;
  status: ScanStatus;
  stage: string;
  progress: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  report: ScanReport | null;
  error: string | null;
}

export interface ScanHistoryItem {
  id: string;
  input_target: string;
  domain: string;
  profile: ScanProfile;
  status: ScanStatus;
  created_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  score: number | null;
  risk_level: RiskLevel | null;
  confidence: ConfidenceLevel | null;
  coverage_percent: number | null;
  error: string | null;
}

export interface ScanHistoryPage {
  items: ScanHistoryItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ScanChanges {
  scan_id: string;
  previous_scan_id: string | null;
  score_delta: number | null;
  added_findings: string[];
  resolved_findings: string[];
  added_ports: number[];
  removed_ports: number[];
  added_subdomains: string[];
  removed_subdomains: string[];
  certificate_changed: boolean;
}
