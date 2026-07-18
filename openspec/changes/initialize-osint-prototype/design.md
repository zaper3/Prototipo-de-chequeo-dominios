# Design

## Approach

React consulta trabajos FastAPI mediante polling. El backend valida el dominio y la resolución pública antes de lanzar tareas concurrentes; cada fuente devuelve datos normalizados o un error parcial. El escaneo TCP usa workers limitados y termina al alcanzar el plazo global. Una función determinista transforma evidencias en score y hallazgos.

## Security Decisions

- Contrato `authorized: true` y confirmación equivalente en UI.
- Solo dominio, nunca URL o IP directa; bloqueo de cualquier resolución no global.
- Sin redirects HTTP automáticos para evitar pivotar a destinos internos.
- Sin persistencia ni logging deliberado de resultados sensibles.
- Proveedores mediante entorno y degradación limpia si no están configurados.

## Verification

Pruebas unitarias de validación, bloqueo y evaluación; prueba de UI para autorización; build TypeScript; smoke test manual de salud, creación, polling y navegación por resultados.
