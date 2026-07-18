# Contribución y flujo de cambio

Aunque el proyecto es personal, todo cambio debe poder retomarse y auditarse sin depender del historial de conversación.

1. Crea o actualiza un cambio en `openspec/changes/<verbo>-<capacidad>/` con propuesta, delta de requisitos, diseño y tareas.
2. Trabaja en una rama `feat/…`, `fix/…`, `docs/…` o `chore/…`; usa commits convencionales.
3. Añade pruebas para el comportamiento nuevo o corregido y actualiza `CHANGELOG.md` bajo `Unreleased`.
4. Registra defectos en `docs/registers/BUGS.md`; al resolverlos, enlaza su entrada en `FIXES.md`.
5. Abre una PR, verifica CI y compara código, pruebas y especificación antes de fusionar.
6. Prepara una candidata según `docs/RELEASE_MANAGEMENT.md`; etiqueta la versión estable solo tras superar sus criterios.

No incluyas claves, datos personales, resultados sensibles ni dominios analizados en commits, fixtures o incidencias.
