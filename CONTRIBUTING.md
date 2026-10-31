# Contribución y flujo de cambio

Aunque el proyecto es personal, todo cambio debe poder retomarse y auditarse sin depender del historial de conversación.

1. Crea o actualiza un cambio en `openspec/changes/<verbo>-<capacidad>/` con propuesta, delta de requisitos, diseño y tareas.
2. Trabaja en una rama `feat/…`, `fix/…`, `docs/…` o `chore/…`; usa commits convencionales.
3. Añade pruebas para el comportamiento nuevo o corregido y actualiza `CHANGELOG.md` bajo `Unreleased`.
4. Registra defectos en `docs/registers/BUGS.md`; al resolverlos, enlaza su entrada en `FIXES.md`.
5. Abre una PR, verifica CI y compara código, pruebas y especificación antes de fusionar.
6. Prepara una candidata según [gestión de releases](docs/RELEASE_MANAGEMENT.md); etiqueta solo tras superar sus criterios y contar con autorización de publicación. Un commit documental no exige nueva release ni mover tags.

En este equipo utiliza la ubicación canónica de [README](README.md), no el checkout retirado de OneDrive. Ejecuta Python como módulo desde `backend/`; comprueba versiones y enlaces con `node scripts/check-docs.mjs`, y valida OpenSpec antes de la PR. Las dependencias se reinstalan desde requirements y `npm ci`; no se migran copiando caches o `.venv`.

Mantén diferenciados: validación local, CI remoto, revisión visual, prueba con terceros y aprobación de publicación. Una prueba no realizada debe constar como `NOT_RUN`, no como aprobada.

No incluyas claves, datos personales, resultados sensibles ni dominios analizados en commits, fixtures o incidencias.

Para presentación del repositorio, sigue la [guía reutilizable ES/EN](docs/README_STYLE_GUIDE.md): mantén ambos README equivalentes y etiqueta la procedencia de las capturas. Ejecuta `node scripts/docs/check-readme.mjs` cuando cambien README, fixtures o medios; no uses historial privado para preparar imágenes.
