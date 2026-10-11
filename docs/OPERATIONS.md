# Operación, DevOps e ITIL

## Modelo operativo local

- Servicio local para un único operador autorizado; no apto para exposición pública.
- Checkout canónico de este equipo: `C:\Users\Usuario\Documents\Visual Studio Projects\Prototipo de chequeo dominios`. La copia OneDrive está retirada; [evidencia de consolidación](WORKSPACE_AUDIT_2026-10-11.md).
- `GET /api/v1/health` publica estado y versión; `/docs` publica OpenAPI.
- Uvicorn registra accesos/excepciones y SQLite conserva informes 90 días. No compartas logs/errores sin revisar: no hay redacción de secretos garantizada.
- Un análisis profundo a la vez es la recomendación, no una exclusión automática. Tiempo de puertos, sockets, rate limit y concurrencia TCP son configurables; no hay timeout global del trabajo.

## Ciclo DevOps

1. **Plan:** propuesta OpenSpec con alcance, riesgos y reversión.
2. **Code:** cambio pequeño y contrato compatible cuando sea posible.
3. **Build/Test:** Ruff, `python -m pytest`, migración Alembic, Vitest, build, `node scripts/check-docs.mjs` y validación OpenSpec.
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

1. Abre el checkout canónico y, si necesitas configuración personalizada, copia `.env.example` a `.env` sin sobrescribir una configuración existente. Evita introducir tokens en URLs.
2. En `backend`, crea/activa una `.venv` nueva con Python instalado, instala `requirements-dev.txt` y ejecuta `python -m alembic upgrade head`. No copies entornos virtuales: pueden apuntar a la ubicación anterior o a intérpretes temporales.
3. Inicia `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`; confirma `/api/v1/health`. En `frontend`, ejecuta `npm ci` y `npm run dev -- --host 127.0.0.1`.
4. Un smoke sin terceros verifica salud, historial y frontend sin crear escaneos. Para probar recopilación, usa un dominio expresamente autorizado; incluso rápido realiza TLS/HTTP. Profundo requiere confirmación adicional.
5. Revisa `errors`, cobertura y confianza: una fuente caída produce un informe parcial utilizable.
6. Antes de actualizar, crea un respaldo consistente mediante la API de backup de SQLite (ver abajo), o detén todos los escritores y copia `data/domaincheck.db` con WAL/SHM como una unidad. Copiar solo `.db` con WAL activo puede perder transacciones.
7. Para revertir código, vuelve a un commit/tag compatible conocido. La candidata 0.1 no tiene tag. No hagas downgrade de esquema sin respaldo probado.

Al reiniciar, los trabajos `queued` o `running` quedan `interrupted`. La limpieza de retención se ejecuta al arrancar y tras completar análisis. No se reanudan tareas interrumpidas automáticamente.

## Respaldo y restauración

Desde la raíz, con Python instalado:

```powershell
python scripts/backup-history.py data/domaincheck.db data/backup-manual.db
```

El destino debe ser nuevo. El helper abre la fuente en modo solo lectura, incluye transacciones WAL confirmadas y verifica integridad y cantidad de registros. Los respaldos están excluidos de Git y no se purgan automáticamente: su retención es responsabilidad del operador.

Para restaurar, detén los servicios y verifica que no haya escritores; conserva el conjunto actual DB/WAL/SHM en una carpeta de recuperación. Instala una copia del respaldo como `data/domaincheck.db` sin dejar WAL/SHM de otra base, ejecuta Alembic y comprueba el historial. No uses una restauración para sobrescribir informes más recientes sin contrastarlos.

En una migración de directorio, compara HEAD, cambios locales, archivos por hash, configuración y contenido lógico SQLite; materializa placeholders de OneDrive y reconstruye dependencias. No elimines el origen hasta verificar funcionamiento desde el destino y sincronización remota.

## Incidentes

- **P1:** acceso a red privada, fuga de secreto, corrupción/pérdida de base o uso no autorizado. Detener, preservar evidencia mínima y rotar claves.
- **P2:** scoring sustancialmente incorrecto, migración fallida o indisponibilidad total. Desactivar la función y preparar fix.
- **P3/P4:** fuente parcial, defecto visual o documental. Registrar y priorizar.
