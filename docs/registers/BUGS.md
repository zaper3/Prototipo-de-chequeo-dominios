# Registro de bugs

| ID | Fecha | Estado | Severidad | Componente | Descripción | Reproducción | Versión | Fix |
|---|---|---|---|---|---|---|---|---|
| `BUG-2026-001` | 2026-07-18 | verified | medium | Validación | Una URL HTTP/HTTPS válida era rechazada por exigir dominio desnudo. | En `0.1`, enviar una URL HTTPS pública con ruta. | `0.1.0-rc.1` local | `FIX-2026-001` |
| `BUG-2026-002` | 2026-07-18 | verified | medium | Alembic | La migración inicial fallaba si `data/` todavía no existía. | En checkout nuevo, ejecutar `alembic upgrade head`. | `0.2.0-alpha.1` | `FIX-2026-002` |
| `BUG-2026-003` | 2026-07-18 | verified | medium | CI | Pytest no encontraba `backend/app` al usar el ejecutable directo en el runner Linux. | Ejecutar el job backend del PR #1. | `0.2.0-alpha.1` | `FIX-2026-003` |
| `BUG-2026-004` | 2026-10-11 | verified | medium | Workspace | Faltaban cuatro deltas OpenSpec en Documents y persistían placeholders cloud. | Comparar inventario Git/hashes y atributos con OneDrive. | checkout de alpha | `FIX-2026-004` |
| `BUG-2026-005` | 2026-10-11 | verified | medium | Entorno | La .venv copiada dependía de un Python temporal inexistente. | Ejecutar Python de la .venv en Documents: uv trampoline no encuentra intérprete. | entorno local | `FIX-2026-005` |
| `BUG-2026-006` | 2026-10-11 | verified | medium | Documentación | Seguridad describía memoria/dominio desnudo; enlaces a tag 0.1 inexistente y capacidades sobredeclaradas. | Contrastar documentación con código, Git y releases remotas. | documentación de alpha | `FIX-2026-006` |
| `BUG-2026-007` | 2026-10-11 | triaged | high | Dependencias dev | npm audit reporta seis paquetes afectados (3 high, 3 moderate). | npm ci y npm audit sobre el lock actual. | `0.2.0-alpha.1` | Pendiente; RISK-010 |
| `BUG-2026-008` | 2026-10-11 | triaged | high | HTTP/SSRF | HTTP resuelve otra vez el hostname después de validar IP. | Inspección de resolve_public_ips y _http_info; no se explotó. | `0.2.0-alpha.1` | Pendiente; RISK-007 |
| `BUG-2026-009` | 2026-10-11 | triaged | high | Privacidad | str(exc) de HTTPStatusError puede incluir una URL de Safe Browsing con clave. | Inspección de _reputation; no se usaron claves reales. | `0.2.0-alpha.1` | Pendiente; RISK-008 |
| `BUG-2026-010` | 2026-10-11 | triaged | medium | Scoring | Datos no recogidos/fallidos pueden interpretarse como control ausente o TLS inválido. | Inspección de fallbacks del scanner y reglas DNSSEC/correo/TLS. | reglas `2.0.0` | Pendiente; RISK-009 |
| `BUG-2026-011` | 2026-10-11 | verified | low | OpenSpec | Los deltas MODIFIED de la alpha omitían escenarios de los specs vigentes; la CLI actual los rechaza. | openspec validate --all --no-interactive. | documentación de alpha | `FIX-2026-007` |

| `BUG-2026-012` | 2026-10-31 | verified | low | QA README | Los hashes binarios de fuentes CRLF en Windows no coincidían con el checkout LF de CI, pese a no cambiar su contenido. | Primer job specification de PR #4: Screenshot inputs changed, App.tsx. | Unreleased / docs | `FIX-2026-008` |

Los fixes de octubre son de checkout, entorno y documentación; no modifican retroactivamente la release alpha. Los defectos del producto identificados quedan pendientes de cambios específicos y pruebas de regresión.

Estados: `new`, `triaged`, `in-progress`, `blocked`, `fixed`, `verified`, `closed`. Severidades: `critical`, `high`, `medium`, `low`.
