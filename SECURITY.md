# Política de seguridad

Revisada el 2026-10-11 para `0.2.0-alpha.1`.

## Modelo de uso

Aplicación defensiva local, de un único operador y solo sobre objetivos autorizados. No debe exponerse a Internet: no hay autenticación ni autorización por activo. Todos los perfiles realizan conexiones activas. Los trabajos e informes se persisten en SQLite; las tareas y el rate limit viven en el proceso y no constituyen una cola duradera.

## Controles incorporados

- Dominios o URLs HTTP/HTTPS; solo se analiza el hostname IDNA. Se rechazan credenciales, IP directa y cualquier puerto explícito, incluso 80/443.
- Antes de recopilar, se rechaza el objetivo si alguna IP resuelta no es global. Un rechazo DNS puede quedar guardado como trabajo fallido.
- TLS y TCP usan una IP previamente validada; HTTP vuelve a resolver el hostname. No se siguen redirects.
- Autorización en API/UI y confirmación adicional para profundo.
- Rate limit por cliente y límites de tiempo/concurrencia de conexiones. `SCAN_MAX_SECONDS` limita la fase de puertos, no el análisis completo; no hay límite global de trabajos simultáneos.
- CORS configurable para el frontend local y cabeceras defensivas de API.
- Claves por entorno, `.env` y datos excluidos de Git; SQLite WAL y retención configurable de 90 días.

## Límites y privacidad

El bloqueo de resoluciones privadas reduce SSRF, pero **no elimina DNS rebinding** en HTTP. No publiques este servicio. Los errores de proveedores se guardan como texto y podrían incluir URLs con claves; no se garantiza redacción automática de secretos. No compartas informes o logs sin revisarlos y mantén deshabilitados los proveedores con claves hasta resolver esta limitación si ese riesgo no es aceptable.

La entrada original (incluida ruta/query de una URL), WHOIS, cookies, cabeceras e informes pueden contener información sensible. Evita URLs con tokens. La base y los respaldos locales no están cifrados; protege el acceso al equipo. Excluirlos de Git no equivale a cifrarlos.

Consulta [riesgos conocidos](docs/registers/KNOWN_RISKS.md). Profundo no explota, autentica, busca secretos, hace crawling extensivo, UDP ni evasión; sus comprobaciones no equivalen a una auditoría web completa.

## Comunicación de vulnerabilidades

El repositorio GitHub es público aunque el uso sea personal. No abras issues con secretos ni datos de objetivos. El operador debe registrar el defecto de forma privada, asignar severidad e impacto y preparar un cambio OpenSpec `fix-*`. No existe un canal externo de reporte privado configurado.

## Condiciones para evolucionar

Los fixes de producto requieren pruebas de regresión y la versión SemVer correspondiente. La aplicación debe permanecer enlazada a `127.0.0.1` hasta incorporar autenticación, autorización por alcance, protección de datos, cola duradera y endurecimiento SSRF.
