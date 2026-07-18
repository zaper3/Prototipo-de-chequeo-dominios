# Operación, DevOps e ITIL

## Modelo operativo local

- Servicio local para un único operador autorizado; no apto para exposición pública.
- `GET /api/v1/health` publica estado y versión; `/docs` publica OpenAPI.
- Uvicorn registra accesos y excepciones, nunca secretos. Los informes residen en SQLite 90 días.
- Un análisis profundo a la vez es la recomendación; tiempo, sockets, rate limit y concurrencia son configurables.

## Ciclo DevOps

1. **Plan:** propuesta OpenSpec con alcance, riesgos y reversión.
2. **Code:** cambio pequeño y contrato compatible cuando sea posible.
3. **Build/Test:** Ruff, pytest, migración Alembic, Vitest, build y validación OpenSpec.
4. **Release:** SemVer, changelog, candidata, evidencia y tag inmutable.
5. **Operate:** health check, migración, smoke test autorizado, backups y observación de errores parciales.
6. **Learn:** bugs, fixes y riesgos alimentan el siguiente cambio.

## Prácticas ITIL adaptadas

| Práctica | Registro mínimo | Aplicación |
|---|---|---|
| Cambios | `openspec/changes/` + PR | Riesgo, aceptación, reversión y versión. |
| Incidentes/problemas | `BUGS.md` / `FIXES.md` | Impacto, workaround, causa y prevención. |
| Releases | candidatas + changelog | Evidencia y decisión go/no-go. |
| Configuración | Git, `.env.example`, Alembic | Código, entorno y esquema trazables. |
| Mejora continua | riesgos + OpenSpec | Deuda priorizada convertida en cambio. |

## Runbook

1. Copia `.env.example` a `.env` y revisa límites y claves.
2. En `backend`, instala dependencias y ejecuta `python -m alembic upgrade head`.
3. Inicia Uvicorn y confirma `/api/v1/health`; después inicia Vite.
4. Usa rápido o estándar para smoke test sobre un dominio autorizado. Profundo requiere confirmación adicional.
5. Revisa `errors`, cobertura y confianza: una fuente caída produce un informe parcial utilizable.
6. Antes de actualizar, detén el servicio y respalda `data/domaincheck.db` junto a sus ficheros WAL/SHM.
7. Para revertir código, vuelve al tag anterior. No hagas downgrade de esquema sin respaldo probado.

Al reiniciar, los trabajos que seguían en ejecución quedan `interrupted`. La limpieza de retención se ejecuta al arrancar y tras cada análisis.

## Incidentes

- **P1:** acceso a red privada, fuga de secreto, corrupción/pérdida de base o uso no autorizado. Detener, preservar evidencia mínima y rotar claves.
- **P2:** scoring sustancialmente incorrecto, migración fallida o indisponibilidad total. Desactivar la función y preparar fix.
- **P3/P4:** fuente parcial, defecto visual o documental. Registrar y priorizar.
