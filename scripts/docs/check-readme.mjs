import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const read = (name) => readFileSync(resolve(root, name), "utf8");
const documents = ["README.md", "README.en.md"];
const content = documents.map(read);
const unfenced = (text) => text.replace(/^ *```[^\n]*\n[\s\S]*?^ *```[^\n]*$/gm, "");
const slug = (title) => title.toLowerCase().replace(/[^\p{L}\p{N}\p{M}_ -]/gu, "").replace(/ /g, "-");
const anchors = (text) => {
  const counts = new Map();
  return new Set([...unfenced(text).matchAll(/^#{1,6} +(.+)$/gm)].map((match) => {
    const base = slug(match[1]);
    const count = counts.get(base) || 0;
    counts.set(base, count + 1);
    return base + (count ? "-" + count : "");
  }));
};
let checkedLinks = 0;
for (let index = 0; index < content.length; index++) {
  const text = content[index];
  for (const match of unfenced(text).matchAll(/\[[^\]\n]+\]\(([^)\n]+)\)/g)) {
    const target = match[1];
    if (/^[a-z][a-z0-9+.-]*:/i.test(target)) continue;
    const [path, anchor] = decodeURIComponent(target).split("#");
    const destination = path || documents[index];
    assert(existsSync(resolve(root, destination)), "Missing README target: " + target);
    if (anchor && destination.endsWith(".md")) {
      assert(anchors(read(destination)).has(anchor), "Missing README anchor: " + target);
    }
    checkedLinks++;
  }
  assert(text.includes(index === 0 ? "(README.en.md)" : "(README.md)"), "Missing language switch");
  for (const fact of ["0.2.0-alpha.1", "2.0.0", "RDAP", "1–1024", "1–65535", "90", "DNS rebinding", "127.0.0.1"]) {
    assert(text.includes(fact), "Missing shared fact: " + fact);
  }
  for (const match of read(".env.example").matchAll(/^([A-Z_]+)=/gm)) {
    assert(text.includes(match[1]), "Missing configuration variable: " + match[1]);
  }
}
const commands = (text) => [...text.matchAll(/^ *```powershell\s*\n([\s\S]*?)^ *```/gm)]
  .map((match) => match[1].split(/\r?\n/).map((line) => line.trim()).filter(Boolean).join("\n"));
assert(commands(content[0]).length >= 5, "Expected installation, backup and quality commands");
assert.deepEqual(commands(content[0]), commands(content[1]), "PowerShell commands differ between languages");

const manifest = JSON.parse(read("docs/media/capture-manifest.json"));
assert.equal(manifest.app_version, read("VERSION").trim());
assert.equal(manifest.private_history_accessed, false);
assert.equal(manifest.backend_started, false);
assert.equal(manifest.public_scans, 0);
assert.equal(manifest.external_page_requests, 0);
assert.equal(manifest.page_errors, 0);
const digest = (file) => createHash("sha256").update(readFileSync(resolve(root, file))).digest("hex");
for (const [key, file] of [
  ["app", "frontend/src/App.tsx"], ["styles", "frontend/src/styles.css"],
  ["fixtures", "scripts/docs/readme-fixtures.mjs"],
]) {
  assert.equal(digest(file), manifest.source_sha256[key], "Screenshot inputs changed: " + file);
}
assert.equal(manifest.images.length, 3);
for (const item of manifest.images) {
  assert(/^[a-z-]+\.png$/.test(item.file), "Unexpected image name");
  const file = "docs/media/" + item.file;
  const bytes = readFileSync(resolve(root, file));
  assert.equal(bytes.subarray(0, 8).toString("hex"), "89504e470d0a1a0a");
  assert.equal(digest(file), item.sha256, "Image hash mismatch: " + file);
  assert.equal(bytes.readUInt32BE(16), item.width);
  assert.equal(bytes.readUInt32BE(20), item.height);
  assert(bytes.length < 600_000, "Unexpectedly large README image");
  for (const text of content) assert(text.includes(file), "Image missing from one language: " + file);
}
for (const name of ["cover.svg", "cover.en.svg"]) {
  const svg = read("docs/media/" + name);
  assert(svg.includes("<title") && svg.includes("<desc"), "Cover must have accessible text");
  assert(!/<(?:script|foreignObject)\b|\bon\w+\s*=|\bhref\s*=\s*["']https?:/i.test(svg), "Unsafe active SVG content");
}
console.log("README QA OK: ES/EN command parity, " + checkedLinks + " local links/anchors, 3 verified PNGs, SVG and synthetic-data provenance.");
