# Registro de bugs

| ID | Fecha | Estado | Severidad | Componente | Descripción | Reproducción | Versión | Fix |
|---|---|---|---|---|---|---|---|---|
| `BUG-2026-001` | 2026-07-18 | verified | medium | Validación | Una URL HTTP/HTTPS válida era rechazada por exigir dominio desnudo. | En `0.1`, enviar `https://magisttv.org/`. | `0.1.0-rc.1` | `FIX-2026-001` |
| `BUG-2026-002` | 2026-07-18 | verified | medium | Alembic | La migración inicial fallaba si `data/` todavía no existía. | En checkout nuevo, ejecutar `alembic upgrade head`. | `0.2.0-alpha.1` | `FIX-2026-002` |
| `BUG-2026-003` | 2026-07-18 | verified | medium | CI | Pytest no encontraba `backend/app` al usar el ejecutable directo en el runner Linux. | Ejecutar el job backend del PR #1. | `0.2.0-alpha.1` | `FIX-2026-003` |

Estados: `new`, `triaged`, `in-progress`, `blocked`, `fixed`, `verified`, `closed`. Severidades: `critical`, `high`, `medium`, `low`.
