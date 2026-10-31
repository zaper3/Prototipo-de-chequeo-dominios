# Validación documental — README visual ES/EN

Fecha: **2026-10-31**. Alcance: presentación, traducción, medios, guía reutilizable y soporte de QA. Sin cambios en backend/frontend del producto, dependencias publicadas, versión, licencia, visibilidad, tag o release.

## Información preservada

| Contenido anterior | Ubicación en ambos README |
|---|---|
| Estado alpha, stack, método y uso local/autorizado | Resumen, advertencia y desarrollo/verificación |
| WHOIS, DNS, TLS, HTTP, CT, subdominios, red y reputación | Capacidades y perfiles |
| Rápido/estándar/profundo, confirmaciones y exclusiones | Inicio y tabla de perfiles |
| SQLite WAL, 90 días, interrupciones y datos privados | Datos/configuración y seguridad |
| URL→hostname y riesgo no absoluto | Resumen, capturas e interpretación |
| Instalación Python/npm, Alembic y endpoints | Empezar |
| Variables y APIs opcionales | Tabla de configuración y .env.example enlazada |
| Calidad, OpenSpec, SemVer y changelog | Desarrollo/verificación y mapa documental |
| Ruta Documents, .venv no portable y auditoría anterior | Workspace y documentación |
| Limitaciones y riesgos conocidos | Seguridad y límites, sin presentarlos como resueltos |

Se añade la explicación de categorías/confianza/cobertura y comparación; no se modifica cómo las calcula el producto. README.en.md conserva los cinco bloques de comandos de README.md.

## Medios y privacidad

Portada SVG original y tres capturas del frontend compilado con API simulada. Se inspeccionaron las imágenes; se corrigió el encuadre del resumen para que la barra sticky no tapara su título. No hay capturas del historial privado, claves ni resultados de terceros. Las leyendas distinguen imagen ilustrativa, interfaz real y datos sintéticos.

El [manifiesto](../media/capture-manifest.json) conserva hashes/dimensiones y origen de entradas. El navegador no inició el backend ni envió escaneos. La captura de la UI y el render de los documentos son verificaciones diferentes.

## Comprobaciones locales

| Gate | Resultado |
|---|---|
| Ruff app/tests/migrations/scripts | PASS; 18 archivos con formato comprobado |
| Backend pytest | PASS, 29 tests |
| Frontend Vitest | PASS, 4 tests |
| TypeScript/build frontend | PASS |
| Helper SQLite | PASS, 4 tests |
| Hashes de procedencia Windows/Linux | PASS, 3 tests Node sobre equivalencia LF/CRLF y detección de cambios reales |
| Gate documental global | PASS |
| QA README ES/EN | PASS: comandos, variables, links/anchors, PNG/SVG y hashes de fuentes |
| OpenSpec 1.14.1 | PASS |
| Captura de frontend con fixtures | PASS: preview, historial, reapertura, comparación, DNS, evidencias y resumen sin overflow a 390px |
| Errores de página/peticiones externas en la captura | 0 / 0 |
| Render Markdown de ambos README por GitHub | PASS; HTML local bajo data/, no publicado como interfaz |
| Inspección visual de portada y tres PNG | PASS |
| Datos reales / APIs de proveedores / escaneo público | NOT_RUN |
| Accesibilidad completa y todos los tamaños | NOT_RUN |

Las pruebas mockean fuentes externas. La captura de una vista responsive no constituye certificación de accesibilidad. Tampoco valida el cálculo de riesgo del backend: los scores de las imágenes proceden de fixtures.

## Publicación

Esta acta recoge validaciones locales y una corrección de CI antes de la fusión. El resultado remoto final se consulta en la PR y en [CI](https://github.com/zaper3/Prototipo-de-chequeo-dominios/actions/workflows/ci.yml), sin atribuirlo a pruebas locales.

La [primera CI de PR #4](https://github.com/zaper3/Prototipo-de-chequeo-dominios/actions/runs/41187197766) pasó backend/frontend pero rechazó el hash de App.tsx por CRLF frente a LF, sin cambios de código. BUG-2026-012 / FIX-2026-008 normaliza únicamente texto a LF y añade tres regresiones; los PNG siguen verificándose byte a byte. La procedencia queda explícita en `source_text_normalization`.

Se prepara una entrega documental bajo `Unreleased`, con PR/CI antes de fusionar. El tag `v0.2.0-alpha.1` permanece en `5fe9bd2858f99cd8b654293e744083d8e58ecca9`; no se publica nueva release. Los medios, la guía y los helpers son nuevos; el código del motor y la UI permanecen sin cambios.
