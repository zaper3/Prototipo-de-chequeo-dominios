# Capturas y recursos del README

Actualización: **2026-10-31**. [Español](../../README.md) · [English](../../README.en.md)

## Qué representan

| Archivo | Tipo | Procedencia |
|---|---|---|
| [cover.svg](cover.svg) / [cover.en.svg](cover.en.svg) | Ilustración vectorial original ES/EN | Portadas creadas para DomainCheck; no son capturas ni resultados de análisis. |
| [scan-start.png](scan-start.png) | Captura de ejecución | Frontend compilado, vista previa del hostname y perfiles. |
| [risk-overview.png](risk-overview.png) | Captura de ejecución con datos sintéticos | Resumen, comparación, categorías, recomendaciones y hallazgos ficticios. |
| [scan-history.png](scan-history.png) | Captura de ejecución con datos sintéticos | Tres registros ficticios para mostrar filtros y acciones. |
| [capture-manifest.json](capture-manifest.json) | Evidencia técnica | Fecha, versión del navegador, dimensiones, hashes, comprobaciones y límites. |

**No se escaneó ningún dominio ni se leyó la base privada.** El backend no se arrancó. Se utilizó el frontend real de `0.2.0-alpha.1` con respuestas de API simuladas desde [readme-fixtures.mjs](../../scripts/docs/readme-fixtures.mjs). Los nombres `example.test` y las IP `192.0.2.x` se usan exclusivamente como datos de ejemplo.

El score, las categorías y los hallazgos de estas imágenes no son resultados del motor contra un objetivo. La interfaz actual está en español; el README inglés reutiliza las imágenes con esa advertencia, sin simular una traducción de la aplicación.

## Reproducir

Requiere Node.js 24+, dependencias del frontend y un navegador Chromium compatible. En Windows el helper detecta Edge o Chrome instalado; en otros entornos puede usarse el navegador de Playwright.

Desde la raíz, en PowerShell:

```powershell
Push-Location frontend
npm ci
npm run build
Pop-Location

npm install --prefix data/readme-20261031/runtime playwright@1.64.1 --no-save --package-lock=false --ignore-scripts --no-audit --no-fund
node scripts/docs/capture-readme.mjs
node scripts/docs/check-readme.mjs
```

No instala ni actualiza dependencias del producto: el runtime de captura queda bajo `data/`, ignorado por Git. `DOCS_PLAYWRIGHT_MODULE` permite indicar otro `playwright/index.mjs`; `DOCS_BROWSER_EXECUTABLE`, otro ejecutable de navegador. Si no hay navegador instalado, instálalo con el runtime de Playwright antes de capturar.

El helper inicia un servidor temporal propio en `127.0.0.1`, en un puerto libre, y lo cierra al terminar. Intercepta las consultas API con fixtures; bloquea métodos distintos de GET, endpoints no previstos y peticiones externas. No usa el servidor del operador ni su historial. Las capturas y el manifiesto se regeneran bajo `docs/media/`; el preview de portada queda bajo `data/`.

Se captura inicio a 1440 × 1000; resumen e historial son recortes de elementos. Para el resumen se aumenta la altura del viewport, evitando que la barra sticky oculte el título sin modificar CSS/DOM del producto. Las dimensiones finales de cada PNG están en el manifiesto.

## Verificación y límites

- Render del frontend compilado; hostname anticipado y tres registros de historial.
- Reapertura del informe, comparación anterior, panel DNS y evidencias.
- Ausencia de desbordamiento horizontal a 390 px en el resumen.
- Cero errores de página y cero peticiones externas desde la página.
- Inspección visual de las tres capturas y la portada.
- Hashes binarios de PNG y hashes de texto de fixtures/componente/estilos normalizados a LF, para no confundir CRLF de Windows con cambios de contenido en Linux.
- No prueba la persistencia real, la recopilación de fuentes, la puntuación del backend ni todos los flujos responsive/accesibles.

Las comprobaciones no sustituyen la aceptación del producto ni autorizan escaneos. El verificador documental no navega a terceros ni vuelve a tomar capturas durante CI.

Referencias técnicas: [capturas Playwright](https://playwright.dev/docs/screenshots) e [intercepción de red](https://playwright.dev/docs/network).
