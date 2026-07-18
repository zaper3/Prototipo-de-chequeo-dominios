# Changelog

Todos los cambios relevantes se documentan aquí siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

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
[0.2.0-alpha.1]: https://github.com/zaper3/Prototipo-de-chequeo-dominios/compare/v0.1.0-rc.1...v0.2.0-alpha.1
[0.1.0-rc.1]: https://github.com/zaper3/Prototipo-de-chequeo-dominios/releases/tag/v0.1.0-rc.1
