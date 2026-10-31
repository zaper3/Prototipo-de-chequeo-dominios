// Capture the built frontend with a fully mocked API. Never starts the backend.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createServer } from "node:http";
import { existsSync, readFileSync, statSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, extname, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { changes, history, job } from "./readme-fixtures.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const dist = resolve(root, "frontend/dist");
const output = resolve(root, "docs/media");
const playwrightModule = process.env.DOCS_PLAYWRIGHT_MODULE
  ?? resolve(root, "data/readme-20261031/runtime/node_modules/playwright/index.mjs");
const { chromium } = await import(pathToFileURL(playwrightModule).href);
const browserPath = process.env.DOCS_BROWSER_EXECUTABLE ?? [
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
].find(existsSync);
assert(existsSync(resolve(dist, "index.html")), "Build frontend first");
mkdirSync(output, { recursive: true });
const mime = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml" };
const server = createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
  let file = resolve(dist, "." + pathname);
  if (file !== dist && !file.startsWith(dist + sep)) {
    response.writeHead(403).end(); return;
  }
  if (!existsSync(file) || !statSync(file).isFile()) file = resolve(dist, "index.html");
  response.writeHead(200, { "Content-Type": mime[extname(file)] ?? "application/octet-stream" });
  response.end(readFileSync(file));
});
await new Promise((done, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", done);
});
const origin = "http://127.0.0.1:" + server.address().port;
let browser;
const pageErrors = [];
const forbidden = [];
const apiCalls = [];
try {
  browser = await chromium.launch({ headless: true, ...(browserPath ? { executablePath: browserPath } : {}) });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1,
    locale: "es-ES", timezoneId: "Europe/Madrid", colorScheme: "dark", serviceWorkers: "block",
  });
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) {
      forbidden.push(url.origin);
      await route.abort(); return;
    }
    if (!url.pathname.startsWith("/api/")) { await route.continue(); return; }
    const method = route.request().method();
    apiCalls.push(method + " " + url.pathname);
    // Any unexpected endpoint or method is blocked, including POST /scans.
    assert.equal(method, "GET", "Screenshot flow must never submit a scan");
    let json;
    if (url.pathname === "/api/v1/scans") {
      let items = history.filter((item) => !url.searchParams.get("query") || item.domain.includes(url.searchParams.get("query")));
      for (const field of ["risk_level", "profile"]) {
        const value = url.searchParams.get(field);
        if (value) items = items.filter((item) => item[field] === value);
      }
      const offset = Number(url.searchParams.get("offset") || 0);
      const limit = Number(url.searchParams.get("limit") || 10);
      json = { items: items.slice(offset, offset + limit), total: items.length, limit, offset };
    } else if (url.pathname === "/api/v1/scans/docs-current") json = job;
    else if (url.pathname === "/api/v1/scans/docs-current/changes") json = changes;
    else { forbidden.push(method + " " + url.pathname); await route.abort(); return; }
    await route.fulfill({ json });
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(origin, { waitUntil: "networkidle" });
  await page.getByLabel("Dominio o URL").fill("https://example.test/ruta");
  assert.match(await page.locator(".normalization-hint").innerText(), /example\.test/);
  await page.screenshot({ path: resolve(output, "scan-start.png"), fullPage: true, animations: "disabled" });
  await page.getByRole("button", { name: /Historial/ }).click();
  await page.locator(".history-list article").first().waitFor();
  assert.equal(await page.locator(".history-list article").count(), 3);
  await page.locator(".history-panel").screenshot({ path: resolve(output, "scan-history.png"), animations: "disabled" });
  await page.locator(".history-main").first().click();
  await page.locator(".comparison-card").waitFor();
  assert.match(await page.locator(".risk-summary").innerText(), /datos ficticios/);
  // Keep the dashboard in view without the sticky topbar covering its heading.
  await page.setViewportSize({ width: 1440, height: 2400 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.locator(".dashboard").screenshot({ path: resolve(output, "risk-overview.png"), animations: "disabled" });
  await page.getByRole("button", { name: "DNS y correo", exact: true }).click();
  assert.match(await page.locator(".record-groups").innerText(), /192\.0\.2\.10/);
  await page.getByRole("button", { name: "Evidencias", exact: true }).click();
  assert.match(await page.locator(".coverage-block").innerText(), /reputation/);
  // Responsive smoke: no new public asset; verify at phone width as well.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Resumen", exact: true }).click();
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
  assert.equal(horizontalOverflow, false, "Unexpected horizontal overflow at 390px");
  await page.setViewportSize({ width: 1280, height: 360 });
  await page.setContent('<html><body style="margin:0">' + readFileSync(resolve(output, "cover.svg"), "utf8") + "</body></html>");
  await page.screenshot({ path: resolve(root, "data/readme-20261031/cover-preview.png"), animations: "disabled" });
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(forbidden, []);
  const digest = (name) => createHash("sha256").update(readFileSync(resolve(root, name))).digest("hex");
  const manifest = {
    capture_date: "2026-10-31", app_version: "0.2.0-alpha.1",
    mode: "Built application UI with synthetic API fixtures; not a real domain scan",
    browser_version: browser.version(), viewport: { width: 1440, height: 1000 },
    private_history_accessed: false, backend_started: false, public_scans: 0,
    external_page_requests: forbidden.length, page_errors: pageErrors.length,
    checks: ["hostname-preview", "history", "report-reopening", "comparison", "dns", "evidence", "responsive-390px"],
    source_sha256: {
      app: digest("frontend/src/App.tsx"), styles: digest("frontend/src/styles.css"),
      fixtures: digest("scripts/docs/readme-fixtures.mjs"),
    },
    images: ["scan-start.png", "risk-overview.png", "scan-history.png"].map((name) => ({
      file: name, sha256: digest("docs/media/" + name),
      width: readFileSync(resolve(output, name)).readUInt32BE(16),
      height: readFileSync(resolve(output, name)).readUInt32BE(20),
    })),
  };
  writeFileSync(resolve(output, "capture-manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  console.log(JSON.stringify({ screenshots: manifest.images.length, checks: manifest.checks, api_calls: apiCalls.length, page_errors: pageErrors.length, public_scans: 0 }));
} finally {
  if (browser) await browser.close();
  await new Promise((done) => server.close(done));
}
