# Development workspace

On this Windows workstation the canonical checkout, established on 2026-10-11, is:

`C:\Users\Usuario\Documents\Visual Studio Projects\Prototipo de chequeo dominios`

The former OneDrive checkout is a retired recovery copy. Do not edit, serve, commit or publish from it. For other machines, use their own selected checkout; the repository is otherwise portable. Open `DomainCheck.code-workspace` from the canonical location. Reopening the editor/Codex project is necessary if its session still uses the old directory.

## Work and verification

- Preserve user changes, SQLite history, configuration and local backups; never commit `data/`, credentials or target reports.
- Read the relevant OpenSpec change and update affected documentation, changelog and registers.
- Run Python from `backend/` using its newly created `.venv`: `python -m ruff check app tests migrations`, `python -m ruff format --check app tests migrations`, `python -m pytest`, `python -m alembic upgrade head`. Validate migrations against a disposable database when auditing.
- From `frontend/`: `npm ci`, `npm test`, `npm run build`.
- From the root: `node scripts/check-docs.mjs`, `python -m unittest discover -s scripts/tests`, `python -m ruff check scripts`, `python -m ruff format --check scripts`, `npx -y @fission-ai/openspec@1.14.1 validate --all --no-interactive`.
- Tests must mock external collection. Do not scan public domains without explicit scope authorization; quick also generates traffic.
- Bind services to loopback. Record NOT_RUN separately for visual, real-target and external-provider checks not performed.
- Commits, push/merge and release publication need user authorization for the corresponding action. Published tags are immutable. Documentation-only work does not automatically bump the product or create a release.

See [workspace audit](docs/WORKSPACE_AUDIT_2026-10-11.md), [operations](docs/OPERATIONS.md) and [known risks](docs/registers/KNOWN_RISKS.md).
