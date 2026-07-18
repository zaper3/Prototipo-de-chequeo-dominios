# Registro de fixes

| ID | Bug | Fecha | Causa raíz | Cambio | Prueba de regresión | Versión | Verificado por |
|---|---|---|---|---|---|---|---|
| `FIX-2026-001` | `BUG-2026-001` | 2026-07-18 | El contrato aceptaba únicamente sintaxis de dominio. | Normalización segura de URL, conservación de entrada y extracción exclusiva del hostname. | `test_normalize_domain_or_url`, rechazo de credenciales/puertos/IP. | `0.2.0-alpha.1` | pytest + smoke API |
| `FIX-2026-002` | `BUG-2026-002` | 2026-07-18 | Alembic abría SQLite antes de crear su directorio padre. | Crear de forma idempotente el padre de la base antes de conectar. | Migración nueva `20260718_0001` y `alembic current`. | `0.2.0-alpha.1` | ejecución local limpia |
| `FIX-2026-003` | `BUG-2026-003` | 2026-07-18 | El entrypoint `pytest` no incorporó el cwd al path de importación en Linux. | Ejecutar `python -m pytest` y `python -m alembic` en GitHub Actions. | Job backend del PR #1. | `0.2.0-alpha.1` | CI GitHub Actions |
