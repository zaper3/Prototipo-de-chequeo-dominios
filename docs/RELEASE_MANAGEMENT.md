# Gestión de versiones, fixes y candidatas

## Política SemVer

La API pública es `/api/v1` y su esquema OpenAPI. Durante `0.y.z` el producto está en desarrollo inicial:

- `0.MINOR.0`: capacidad nueva o cambio relevante de contrato.
- `0.y.PATCH`: corrección compatible sin capacidad nueva.
- `-alpha.N`: exploración incompleta.
- `-beta.N`: funcionalidad completa con validación pendiente.
- `-rc.N`: candidata funcional con alcance congelado; solo admite fixes.
- `1.0.0`: contrato estable, operación soportada y criterios de producción cumplidos.

Los tags Git usan prefijo `v`, por ejemplo `v0.2.0-alpha.1`; el valor de versión en `VERSION`, backend, frontend y package-lock debe coincidir con una entrada del changelog. `node scripts/check-docs.mjs` comprueba estos valores y enlaces locales.

La única release publicada, verificada el 2026-10-11, es `0.2.0-alpha.1` sobre `5fe9bd2858f99cd8b654293e744083d8e58ecca9`. `0.1.0-rc.1` fue una candidata local sustituida, sin tag/release publicada. No se deben inventar enlaces a tags inexistentes.

Los commits exclusivamente documentales, de CI o de entorno pueden permanecer en `Unreleased` conservando la versión del producto. No muevas un tag publicado ni reedites su contenido para hacer que apunte a un commit posterior. Una nueva release necesita su propio gate; sincronizar documentación no publica automáticamente `0.2.0-rc.1`.

## Criterios de candidata

- Cambio OpenSpec completo y tareas cerradas.
- CI verde en backend y frontend.
- Smoke test UI/API y prueba de cada sección con datos reales autorizados.
- Revisión de dependencias, secretos y controles SSRF; registrar alertas y aceptación explícita, no equiparar CI verde con ausencia de vulnerabilidades.
- Bugs críticos/altos en cero o con aceptación explícita en riesgos conocidos.
- Changelog, versión y registro de candidata actualizados.
- Migración Alembic validada sobre base nueva y respaldo/reversión documentados.
- Plan de reversión: detener servicios, preservar la base y volver al tag anterior compatible.

## Flujo de defectos y fixes

1. Asigna `BUG-YYYY-NNN`, severidad, pasos, impacto y evidencia no sensible.
2. Triage: incidente, problema o defecto ordinario; decide workaround.
3. Crea `openspec/changes/fix-<comportamiento>` cuando cambie un requisito o control.
4. Añade una prueba que falle antes del fix y pase después.
5. Registra `FIX-YYYY-NNN`, relación con bug, causa raíz y versión objetivo.
6. Actualiza `Unreleased`, publica patch/RC y cierra solo tras verificación.

Para un defecto de documentación/entorno, registra fecha, commit y evidencia sin atribuir el fix a un tag inmutable anterior. La auditoría de octubre no sustituye las pruebas visuales o de proveedores externos que requiera la siguiente release.
