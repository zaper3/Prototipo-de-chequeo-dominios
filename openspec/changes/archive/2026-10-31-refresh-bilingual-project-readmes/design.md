# Design

## Information architecture

README.md en español es la entrada principal; README.en.md presenta los mismos hechos, defaults, comandos y límites. Portada SVG propia con marca DomainCheck; tres PNG reales del frontend compilado, claramente descritos como fixtures. Se toma la estructura del ejemplo, no sus imágenes ni afirmaciones de producto/licencia.

La guía README_STYLE_GUIDE.md conserva un esqueleto portable para otros proyectos. No instala una skill ni modifica preferencias globales.

## Privacy and capture

Servidor estático temporal en loopback/puerto libre. Playwright con contexto aislado y API GET simulada; cualquier otro método, endpoint o petición externa se bloquea. Nunca se inicia backend ni se abre data/domaincheck.db. Nombres example.test, direcciones TEST-NET y scores ficticios. Portada vectorial explícitamente ilustrativa.

El manifiesto registra fecha, versión, hashes y dimensiones, sin paths personales del runtime. Se comprueba preview, historial, reapertura/comparación, DNS, evidencias y ausencia de overflow a 390px; no se atribuye validación de motor, persistencia, escaneo ni accesibilidad completa.

## Documentation verification

El gate actual sigue validando versiones/enlaces/OpenSpec. check-readme añade anchors locales, presencia de configuración, paridad de comandos, firma/hashes PNG y procedencia/sincronía de medios. No requiere navegador ni servicios externos en CI. Revisión visual separada mediante previews locales y render GFM cuando disponible.

## Publication

Solo archivos documentales, recursos y helpers de QA. Versión 0.2.0-alpha.1 sin retag ni release. Commit/PR autorizados por el usuario; verificar CI antes de fusionar y dejar master local/remoto sincronizados. Las validaciones previas a la PR no se presentan como CI ya aprobada.
