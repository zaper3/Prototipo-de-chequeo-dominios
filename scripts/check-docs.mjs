import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const read = (name) => readFileSync(join(root, name), "utf8");
const version = read("VERSION").trim();
const packageJson = JSON.parse(read("frontend/package.json"));
const lock = JSON.parse(read("frontend/package-lock.json"));
const backendVersion = read("backend/app/__init__.py").match(/__version__\s*=\s*"([^"]+)"/)?.[1];
for (const [name, value] of Object.entries({
  backend: backendVersion, frontend: packageJson.version,
  lock: lock.version, lockRoot: lock.packages[""].version,
})) {
  if (value !== version) errors.push(`Version mismatch: ${name}=${value}, VERSION=${version}`);
}
if (!/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/.test(version)) {
  errors.push("VERSION must have SemVer syntax");
}
if (!read("CHANGELOG.md").includes(`## [${version}]`)) errors.push("Missing version in changelog");

// Git inventory catches tracked specification files missing from the worktree.
const tracked = execFileSync("git", ["ls-files", "-z"], { cwd: root, encoding: "utf8" }).split("\0").filter(Boolean);
for (const name of tracked) {
  if (!existsSync(join(root, name))) errors.push(`Missing tracked file: ${name}`);
}
const ignored = new Set([".git", ".venv", "node_modules", "data", "dist", "__pycache__", ".pytest_cache", ".ruff_cache"]);
const markdown = [];
function walk(folder) {
  for (const entry of readdirSync(folder, { withFileTypes: true })) {
    if (ignored.has(entry.name) || entry.isSymbolicLink()) continue;
    const path = join(folder, entry.name);
    if (entry.isDirectory()) walk(path);
    else if (entry.isFile() && entry.name.endsWith(".md")) markdown.push(path);
  }
}
walk(root);
let links = 0;
for (const path of markdown) {
  const body = readFileSync(path, "utf8").replace(/^```[^\n]*\n[\s\S]*?^```/gm, "");
  const definitions = new Map();
  for (const match of body.matchAll(/^\[([^\]]+)\]:\s*(\S+)/gm)) definitions.set(match[1].toLowerCase(), match[2]);
  const targets = [...body.matchAll(/\[[^\]\n]+\]\(<?([^)>\n]+)>?\)/g)].map((m) => m[1]);
  targets.push(...definitions.values());
  for (const match of body.matchAll(/\[([^\]\n]+)\]\[([^\]\n]*)\]/g)) {
    const key = (match[2] || match[1]).toLowerCase();
    if (!definitions.has(key)) errors.push(`Undefined reference in ${path}: ${key}`);
  }
  for (const target of targets) {
    if (/^(?:[a-z][a-z0-9+.-]*:|#)/i.test(target)) continue;
    const local = decodeURIComponent(target.split("#")[0].split("?")[0]);
    if (local && !existsSync(resolve(dirname(path), local))) errors.push(`Broken link in ${path}: ${target}`);
    links++;
  }
}
for (const change of readdirSync(join(root, "openspec/changes"), { withFileTypes: true })) {
  if (!change.isDirectory() || change.name === "archive") continue;
  const folder = join(root, "openspec/changes", change.name);
  for (const name of ["proposal.md", "design.md", "tasks.md", "specs"]) {
    if (!existsSync(join(folder, name))) errors.push(`Incomplete OpenSpec change ${change.name}: ${name}`);
  }
}
if (errors.length) {
  process.stderr.write(errors.join("\n") + "\n");
  process.exitCode = 1;
} else {
  process.stdout.write(`Documentation OK: version ${version}, ${markdown.length} Markdown files, ${links} local links, ${tracked.length} tracked files.\n`);
}
