# Arquitectura

## Vista general

```text
React :5173 ── POST/GET/DELETE /api/v1/scans ──► FastAPI :8000
                                                     │
                  SQLite + WAL ◄── SQLAlchemy/Alembic┤
                                                     ├── identidad / DNS y correo
                                                     ├── TLS / HTTP / reputación
                                                     ├── CT / subdominios
                                                     └── red TCP según perfil
```

El frontend presenta estado, historial y resultados. FastAPI normaliza el hostname, impide objetivos no públicos, ejecuta módulos según el perfil y persiste cada transición. OpenAPI bajo `/api/v1` es el contrato canónico.

## Flujo

1. El usuario introduce un dominio o URL y confirma autorización; profundo requiere una segunda confirmación.
2. El backend conserva la entrada, extrae/normaliza el hostname IDNA y valida todas sus resoluciones.
3. Crea un registro UUID y ejecuta solo los módulos del perfil rápido, estándar o profundo.
4. Cada fuente devuelve evidencia normalizada o un error parcial; los fallos opcionales reducen cobertura, no score.
5. El motor `2.0.0` calcula identidad/reputación (35 %), web/TLS (25 %), DNS/correo (20 %) y red (20 %).
6. Persiste el informe JSON, score, riesgo, confianza, cobertura, duración y comparación con el informe anterior.
7. La UI puede reabrir, repetir, filtrar, comparar o borrar. La retención automática es de 90 días.

## Persistencia y recuperación

- `data/domaincheck.db`, fuera de Git, con SQLite WAL y transacciones cortas.
- Alembic mantiene el esquema; `alembic upgrade head` es obligatorio antes de una release.
- Al iniciar, los trabajos `running` se marcan `interrupted` y se eliminan filas vencidas.
- La base no está cifrada; el alcance actual presupone un equipo local con acceso controlado.

## Decisiones de seguridad

- Se conserva la URL original solo como contexto; red, DNS y reputación reciben exclusivamente el hostname validado.
- Los redirects no se siguen automáticamente hacia destinos no revalidados.
- Estándar limita puertos; profundo usa TCP completo y banners seguros con timeout y concurrencia acotados.
- No hay explotación, autenticación, búsqueda de secretos, crawling amplio, UDP ni evasión.
- La puntuación es heurística versionada y nunca una certificación de seguridad.

## Evolución futura

Un despliegue compartido exige autenticación, autorización por alcance, cifrado o base gestionada, cola duradera, cancelación, auditoría y controles de cuota. Una auditoría web activa debe nacer como cambio OpenSpec separado.
