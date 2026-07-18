import type {
  RiskLevel,
  ScanChanges,
  ScanHistoryPage,
  ScanJob,
  ScanProfile,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : "La API no pudo completar la solicitud.";
    throw new Error(detail);
  }
  return payload as T;
}

export async function createScan(target: string, profile: ScanProfile): Promise<ScanJob> {
  const response = await fetch(`${API_BASE}/api/v1/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target,
      profile,
      authorized: true,
      deep_authorized: profile === "deep",
    }),
  });
  return parseResponse<ScanJob>(response);
}

export async function getScan(id: string): Promise<ScanJob> {
  const response = await fetch(`${API_BASE}/api/v1/scans/${id}`, { cache: "no-store" });
  return parseResponse<ScanJob>(response);
}

export async function listScans(filters: { query?: string; riskLevel?: RiskLevel | ""; profile?: ScanProfile | ""; dateFrom?: string; dateTo?: string; limit?: number; offset?: number } = {}): Promise<ScanHistoryPage> {
  const params = new URLSearchParams({ limit: String(filters.limit ?? 10), offset: String(filters.offset ?? 0) });
  if (filters.query) params.set("query", filters.query);
  if (filters.riskLevel) params.set("risk_level", filters.riskLevel);
  if (filters.profile) params.set("profile", filters.profile);
  if (filters.dateFrom) params.set("date_from", `${filters.dateFrom}T00:00:00Z`);
  if (filters.dateTo) params.set("date_to", `${filters.dateTo}T23:59:59Z`);
  const response = await fetch(`${API_BASE}/api/v1/scans?${params}`, { cache: "no-store" });
  return parseResponse<ScanHistoryPage>(response);
}

export async function getChanges(id: string): Promise<ScanChanges> {
  const response = await fetch(`${API_BASE}/api/v1/scans/${id}/changes`, { cache: "no-store" });
  return parseResponse<ScanChanges>(response);
}

export async function deleteScan(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/scans/${id}?confirm=true`, { method: "DELETE" });
  await parseResponse<{ deleted: number }>(response);
}

export async function deleteAllScans(): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/scans`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirm: true }),
  });
  await parseResponse<{ deleted: number }>(response);
}
