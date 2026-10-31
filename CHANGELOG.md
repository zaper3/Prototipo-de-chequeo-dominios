# Changelog

Todos los cambios relevantes se documentan aquí siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

### Changed

- 2026-10-31: README principal en español y README.en.md equivalente, con portada original, capturas del frontend con datos sintéticos, navegación y guía reutilizable.
- Comprobación de paridad de comandos, anchors y procedencia de medios; sin cambios del motor, versión, licencia o release.

- 2026-10-11: checkout canónico trasladado a Documents; retirado el uso de la copia OneDrive, con respaldos locales de código, Git e historial.
- Restaurados cuatro archivos OpenSpec ausentes en la copia destino y reconstruidos los entornos Python/npm; archivos del checkout convertidos en archivos locales sin placeholders cloud.
- Documentación alineada con SQLite, URLs, alcance real de perfiles, scoring y limitaciones de seguridad; candidata local 0.1 identificada como sustituida.
- Verificación documental de versiones/enlaces/especificaciones integrada en CI, guía de workspace portable y respaldo SQLite consistente.
- Registradas alertas de dependencias y deuda del producto sin cambiar el motor ni retaggear la alpha.

## [0.2.0-alpha.1] - 2026-07-18

### Added

- Historial SQLite con retención de 90 días, reapertura, repetición, filtros, comparación y borrado.
- Perfiles rápido, estándar y profundo con alcance de red explícito.
- Subpuntuaciones versionadas, cobertura, confianza y categorías de riesgo comprensibles.
- Hallazgos con identificador, evidencia, fuente, impacto, recomendación y referencia.
- Enriquecimientos opcionales Google Safe Browsing y MDN Observatory.

### Changed

- El objetivo acepta dominio o URL HTTP/HTTPS y analiza exclusivamente su hostname normalizado.
- La API `/api/v1/scans` persiste trabajos y expone endpoints de historial y cambios.
- El dashboard separa riesgo, score, cobertura y confianza.

### Fixed

- La CI invoca pytest y Alembic como módulos para resolver correctamente `backend/app` en Linux.

### Security

- El perfil profundo requiere una segunda confirmación y mantiene fuera de alcance explotación, secretos, UDP, evasión y crawling extensivo.

## [0.1.0-rc.1] - 2026-07-18

Candidata local histórica, sustituida por la alpha; no se publicó tag ni release `v0.1.0-rc.1`.

### Added

- API FastAPI asíncrona para ejecutar y consultar análisis en memoria.
- Recopilación WHOIS, DNS, TLS, HTTP, CT logs, subdominios activos e IP.
- Escaneo completo de puertos TCP de la IP pública principal.
- Evaluación básica de seguridad con puntuación, grado, hallazgos y recomendaciones.
- Proveedores opcionales VirusTotal y SecurityTrails.
- Dashboard React responsive, accesible y organizado por secciones.
- Contratos OpenSpec, documentación operativa y automatización de calidad.

### Security

- Confirmación explícita de autorización, validación estricta del dominio, bloqueo de IP privada/reservada, rate limit y límites de concurrencia/tiempo.

[Unreleased]: https://github.com/zaper3/Prototipo-de-chequeo-dominios/compare/v0.2.0-alpha.1...HEAD
[0.2.0-alpha.1]: https://github.com/zaper3/Prototipo-de-chequeo-dominios/releases/tag/v0.2.0-alpha.1
[0.1.0-rc.1]: openspec/changes/initialize-osint-prototype/
