# Política de seguridad

## Modelo de uso

La herramienta está diseñada para análisis defensivo local y autorizado. No debe exponerse directamente a Internet en su configuración actual: no hay autenticación, la cola y los resultados residen en memoria y el escaneo activo permite generar un volumen significativo de conexiones.

## Controles incorporados

- Entrada limitada a nombres de dominio; no acepta URL, puerto, ruta ni credenciales.
- Conversión IDNA y resolución previa del objetivo.
- Rechazo de cualquier resolución no global para reducir SSRF hacia redes internas, loopback o metadatos cloud.
- Confirmación de autorización en el contrato API y en la interfaz.
- Rate limit por cliente, timeout global y concurrencia máxima configurable.
- CORS limitado al frontend local y cabeceras defensivas de API.
- Secretos solo por variables de entorno; `.env` está excluido de Git.

## Comunicación de vulnerabilidades

No publiques secretos ni datos de objetivos. Registra el defecto de forma privada, asigna severidad e impacto, prepara un cambio OpenSpec `fix-*` y publica el fix con incremento SemVer adecuado. Para una futura publicación pública deberá añadirse un canal privado de reporte.

## Riesgos aceptados de la candidata

Consulta el registro vivo en `docs/registers/KNOWN_RISKS.md`. La aplicación debe permanecer enlazada a `127.0.0.1` hasta incorporar autenticación, persistencia segura, cola duradera y control de acceso por objetivo.
