import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ items: [], total: 0, limit: 50, offset: 0 }),
  }));
});

describe("App", () => {
  it("requires explicit authorization before enabling a scan", () => {
    render(<App />);
    const button = screen.getByRole("button", { name: /^analizar$/i });
    fireEvent.change(screen.getByLabelText("Dominio o URL"), { target: { value: "example.com" } });
    expect(button).toBeDisabled();
    fireEvent.click(screen.getByText(/confirmo que tengo autorización/i));
    expect(button).toBeEnabled();
  });

  it("previews the normalized hostname for a full URL", () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText("Dominio o URL"), { target: { value: "https://example.com/path" } });
    expect(screen.getByText(/la ruta no forma parte/i)).toHaveTextContent("example.com");
  });

  it("requires a second confirmation for the deep profile", () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText("Dominio o URL"), { target: { value: "example.com" } });
    fireEvent.click(screen.getByText(/confirmo que tengo autorización/i));
    fireEvent.click(screen.getByRole("button", { name: /profundo varios min/i }));
    expect(screen.getByRole("button", { name: /^analizar$/i })).toBeDisabled();
    fireEvent.click(screen.getByText(/autorizo el escaneo tcp completo/i));
    expect(screen.getByRole("button", { name: /^analizar$/i })).toBeEnabled();
  });

  it("filters and paginates the persistent history", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [{
          id: "scan-1", input_target: "example.com", domain: "example.com",
          profile: "standard", status: "completed", created_at: "2026-07-18T10:00:00Z",
          completed_at: "2026-07-18T10:01:00Z", duration_seconds: 60, score: 82,
          risk_level: "moderate", confidence: "medium", coverage_percent: 75, error: null,
        }],
        total: 12,
        limit: 10,
        offset: 0,
      }),
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /historial/i }));
    fireEvent.change(screen.getByLabelText("Fecha desde"), { target: { value: "2026-07-01" } });
    await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => String(url).includes("date_from=2026-07-01"))).toBe(true));
    fireEvent.click(await screen.findByRole("button", { name: "Página siguiente" }));
    await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => String(url).includes("offset=10"))).toBe(true));
  });
});
