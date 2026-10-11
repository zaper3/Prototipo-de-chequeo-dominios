# Design

## Canonical checkout

En este equipo, Documents es canónico; OneDrive permanece como recuperación retirada. Un archivo code-workspace relativo evita fijar paths obsoletos. Una sesión de editor/Codex iniciada en la ubicación antigua debe reabrirse explícitamente desde el destino.

## Evidence and data

Contrastar HEAD/remote/tags, estado Git y SHA256 de archivos antes de copiar. Buscar clones por nombre y remote dentro de rutas accesibles y declarar exclusiones; no prometer ausencia absoluta fuera de ese alcance. Comparar SQLite con lectura consistente incluyendo WAL, integridad, filas y digest lógico sin publicar objetivos.

Los placeholders se respaldan y materializan conservando hash; .venv se archiva y recrea con Python instalado. npm ci respeta el lock. Backups y detalle local quedan bajo data/ fuera de Git. Las alertas de dependencias se registran, no se corrigen implícitamente.

## Documentation gate

check-docs valida coincidencia VERSION/backend/frontend/lock/changelog, enlaces locales, archivos tracked existentes y estructura de cambios OpenSpec. No verifica URLs remotas, anchors, cumplimiento semántico completo ni vulnerabilidades; se complementa con OpenSpec y revisión manual.

backup-history abre SQLite en modo read-only, crea exclusivamente un destino nuevo, copia un snapshot con WAL y verifica integridad/filas. Las conexiones se cierran explícitamente para evitar bloqueos Windows.

## Acceptance boundaries

Pruebas con fuentes mock y smoke localhost sin escaneos. Revisión visual actual y proveedores con claves: NOT_RUN. El registro de julio se preserva como histórico. Publicación final por PR/CI; sin tag/release nueva.
