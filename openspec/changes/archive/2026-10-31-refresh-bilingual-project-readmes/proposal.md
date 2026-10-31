# Proposal: Refresh bilingual project READMEs

## Why

El propietario solicita una presentación visual profesional inspirada en su README de referencia, manteniendo toda la información actual, un README principal en español, una traducción inglesa y sincronización local/GitHub. También busca una estructura reutilizable para otros proyectos.

## What Changes

- Reorganizar README.md con portada original, navegación, galería, capacidades, inicio, perfiles, interpretación, configuración, límites, documentación y calidad.
- Añadir README.en.md equivalente, sin presentar la interfaz como traducida.
- Capturar el frontend real con fixtures sintéticos, sin backend, historial privado ni escaneos.
- Añadir guía de estructura reutilizable y comprobaciones de anchors, comandos y procedencia de medios en CI.
- Mantener versión, licencia, visibilidad y tag publicados sin cambios; publicar solo documentación y soporte de captura/QA.

## Out of Scope

Modificar la lógica del producto, traducir la UI, corregir deuda de seguridad/dependencias, crear skills personales, editar otros repositorios, escanear terceros o publicar nueva release.

## Operational Risk and Rollback

Una captura real puede exponer datos privados y un README vistoso puede sobredeclarar seguridad. Se usa API simulada sin arrancar backend y se mantienen advertencias y límites. El runtime de captura queda ignorado bajo data/. Reversión: revertir el commit documental sin tocar SQLite o tags.
