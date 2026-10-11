# Auditoría de workspace — 2026-10-11

## Decisión y alcance

Ubicación canónica de desarrollo en este equipo:

`C:\Users\Usuario\Documents\Visual Studio Projects\Prototipo de chequeo dominios`

La copia `C:\Users\Usuario\OneDrive - Izertis\Documentos\Visual Studio Projects\Prototipo de chequeo dominios` queda retirada, preservada para recuperación. No fue eliminada ni actualizada para continuar desarrollando.

El operador autorizó auditoría, consolidación, documentación y sincronización final con [GitHub](https://github.com/zaper3/Prototipo-de-chequeo-dominios). No pidió nueva release, cambio de visibilidad ni explotación/escaneo de objetivos.

## Comparación inicial

| Elemento | OneDrive | Documents | Conclusión |
|---|---|---|---|
| HEAD/master | 5fe9bd2858f99cd8b654293e744083d8e58ecca9 | Mismo SHA | Ningún código committed más reciente |
| Remote | zaper3/Prototipo-de-chequeo-dominios | Mismo remote | Coincide con master de GitHub al inicio |
| Inventario | 69 tracked | 65 presentes, 4 ausentes | Los 65 comunes coinciden por SHA256 |
| Cambios locales | CHANGELOG marcado M, sin diff lógico | Igual más 4 borrados | Sin contenido único nuevo en archivos comunes |
| Historial SQLite | 3 registros: 2 completed, 1 failed | Mismo contenido | No requiere merge ni sobrescritura |
| Integridad SQLite/backup | ok | ok | Respaldos consistentes con 3 registros |
| Configuración .env | No presente | No presente | No se trasladaron claves |
| Entorno Python | Intérprete temporal ausente | Igual | Recrear .venv, no copiar |

Digest lógico SQLite (tablas/filas ordenadas, incluidos registros WAL): `0d08dba6db2cbdf860b34cef811726badcc0a1b8d4149fa5a3aaa2d80dfdba6a`, igual en ambas. Rango de registros: 2026-07-18. No se incluyen dominios consultados ni informes en este documento público.

## Búsqueda de otras ubicaciones

Se recorrieron **1.065.034 directorios** por nombre y remote Git en la única unidad local montada (C:) y temporales de Usuario. Se encontraron los dos checkouts completos y el remanente:

`C:\Users\Usuario\DocumentosOLD\Visual Studio Projects\Prototipo de chequeo dominios`

El remanente contiene 7.777 archivos: 7.773 de dependencias/caches y cuatro deltas OpenSpec. No tiene VERSION, código principal, base de datos ni archivos dentro de .git (sin HEAD/config). Sus cuatro deltas coinciden por SHA256 con OneDrive original y se respaldaron en `data/migration-20261011/documentos-old/`. No contiene una versión de código más reciente ni historial exclusivo; se preservó sin modificar.

No se encontraron otros checkouts del proyecto dentro del alcance accesible. Las dos carpetas .git copiadas durante la propia auditoría dentro de `materialized/` y `placeholders/` son respaldos, no entornos de desarrollo; la coincidencia de nombre de C: se descartó como falso positivo.

Exclusiones: Windows, Program Files, ProgramData, carpetas protegidas del sistema, AppData general de Usuario (excepto Temp), plugins de Codex, .vscode y directorios de dependencias/caches/builds. Se registraron 37 directorios inaccesibles y 49 directorios reparse no seguidos (principalmente junctions del sistema y fixtures). No se certifican zonas excluidas, archivos comprimidos ni unidades desconectadas. Reporte y script íntegros en `data/migration-20261011/location-audit.json` y `location-audit.ps1`.

## Consolidación realizada

- Respaldos de cada copia, estado Git, history.bundle y conjunto SQLite/WAL/SHM en `data/migration-20261011/onedrive/` y `documents/`.
- Copias SQLite consistentes `consistent.db` en ambas carpetas; comprobación lógica local en `data/migration-20261011/database-audit.json`.
- Restaurados los cuatro deltas ausentes de `initialize-osint-prototype` y `add-history-and-risk-engine`.
- Materializados 302 archivos del checkout/Git/datos conservando SHA256; originales cloud conservados en `data/migration-20261011/placeholders/`.
- .venv anterior archivada en `data/migration-20261011/legacy-venv/`; nueva .venv creada con Python instalado 3.13.15. npm ci conserva el lock.
- Workspace relativo [DomainCheck.code-workspace](../DomainCheck.code-workspace) y [AGENTS](../AGENTS.md) indican el checkout canónico.

Los respaldos privados quedan excluidos de Git, sin cifrado ni purga automática. La nueva copia no depende del origen OneDrive. Este cambio no puede modificar retroactivamente el cwd de una sesión Codex/editor ya abierta: debe reabrirse en Documents.

## Revisión documental y deuda

Revisados README, seguridad, arquitectura, operación, contribución, releases, changelog, todos los registros y cambios/specs OpenSpec. Se distinguen artefactos 0.1 históricos de requisitos vigentes.

Corregidas afirmaciones de memoria/dominio desnudo, enlaces a tag 0.1 inexistente, orden de persistencia/validación, diff calculado a petición, alcance TLS/subdominios y límite de tiempo solo de puertos. No se prometen RDAP, exhaustividad, redacción de claves o inmunidad SSRF.

Los defectos de HTTP/rebinding, privacidad, scoring y dependencias permanecen pendientes en [bugs](registers/BUGS.md) y [riesgos](registers/KNOWN_RISKS.md). npm audit encontró seis paquetes dev afectados (3 high, 3 moderate); npm audit --omit=dev no reportó alertas en esta fecha. No se actualizaron dependencias del producto.

## Evidencia de aceptación

| Gate | Resultado |
|---|---|
| Ruff backend incluidas migraciones | PASS |
| Backend pytest desde Documents | PASS, 29 tests |
| Frontend Vitest desde Documents | PASS, 4 tests |
| Frontend TypeScript/build | PASS |
| Helper respaldo SQLite | PASS, 4 tests; backup real consistente de 3 registros |
| Alembic sobre base nueva aislada | PASS, 20260718_0001 (head) |
| OpenSpec 1.14.1 | PASS, 6 artefactos; corregidos escenarios MODIFIED omitidos |
| Verificador documental | PASS, versiones/enlaces/inventario; integrado en CI |
| Smoke localhost con base aislada | PASS, salud/OpenAPI, frontend HTTP 200, proxy, 3 registros de historial y URL con credenciales rechazada 422 |
| Revisión visual actual | NOT_RUN; UI sin cambios |
| Escaneo de dominio público/proveedores con claves | NOT_RUN |
| CI remoto de consolidación | PASS: backend, frontend y specification en [run 38148973562](https://github.com/zaper3/Prototipo-de-chequeo-dominios/actions/runs/38148973562) |
| Sincronización master tras consolidación | PASS: [PR #2](https://github.com/zaper3/Prototipo-de-chequeo-dominios/pull/2) fusionada; master local/origin idénticos y worktree limpio |

Los servicios del smoke fueron iniciados desde Documents, identificados por proceso/comando y detenidos al terminar; no quedó listener en 5173/8000. La base operativa no se utilizó para el smoke y no se eliminó historial. Evidencia detallada privada en `data/migration-20261011/smoke-results.json`.

## GitHub y release

El repo es público aunque el uso sea personal. La release `v0.2.0-alpha.1` permanece inmutable sobre `5fe9bd2858f99cd8b654293e744083d8e58ecca9`. La consolidación va a Unreleased: no crea `0.2.0-rc.1` ni desplaza el tag.

La consolidación se fusionó mediante [PR #2](https://github.com/zaper3/Prototipo-de-chequeo-dominios/pull/2) el 2026-10-11, con CI de sus tres jobs aprobada. Se verificó master local limpio e idéntico a origin/master en `9160d81c4395f45300be9ea0494792db03228ad5`; el tag alpha permanece sobre su SHA original.

El cierre de este registro y archivo OpenSpec se sincroniza en un commit documental posterior, también mediante PR/CI. Los datos, respaldos, entornos y logs no se publican. Git fsck no detectó corrupción; ambos bundles pasan verificación y el checkout/Git/datos operativos no conservan archivos reparse.

Cambio completado: [OpenSpec archivado](../openspec/changes/archive/2026-10-11-consolidate-local-workspace-and-docs/). Requisitos de entrega incorporados a [delivery-governance](../openspec/specs/delivery-governance/spec.md), sin alterar los módulos de análisis.
