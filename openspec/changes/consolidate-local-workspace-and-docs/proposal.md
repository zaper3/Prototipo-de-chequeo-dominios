# Proposal: Consolidate local workspace and documentation

## Why

El operador retira la ubicación OneDrive y solicita consolidar desarrollo en Documents, contrastar copias con GitHub y actualizar toda la documentación. La copia destino tenía cuatro archivos OpenSpec ausentes, placeholders cloud y una .venv ligada a Python temporal inexistente.

## What Changes

- Auditar ubicaciones y Git antes de elegir una copia; preservar código, configuración e historial.
- Establecer Documents como checkout canónico, con workspace relativo y guía de continuidad.
- Restaurar especificaciones y reconstruir dependencias; verificar independencia del origen.
- Reconciliar guías, candidatas, riesgos y registros con código y evidencia actual.
- Añadir verificación documental a CI y helper de respaldo SQLite consistente.
- Sincronizar mediante PR/CI, manteniendo inmutable la release alpha.

## Out of Scope

Eliminar la copia OneDrive, cambiar el motor de análisis, escanear terceros, actualizar automáticamente dependencias, cambiar visibilidad del repositorio o publicar nueva release. No se modifica la configuración global de Codex/editor ni memorias.

## Operational Risk and Rollback

Un respaldo solo del archivo SQLite con WAL activo puede perder datos; una .venv copiada puede depender del origen. Se preservan ambas copias, Git bundles y backups SQLite consistentes bajo data/. El smoke usa una copia aislada y no borra historial operativo. Reversión documental mediante revert del commit; entornos antiguos archivados, no destruidos.
