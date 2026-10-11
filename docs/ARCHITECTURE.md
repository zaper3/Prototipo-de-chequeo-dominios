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

El frontend presenta estado, historial y resultados. FastAPI normaliza el hostname, valida que las resoluciones iniciales sean públicas, ejecuta módulos según el perfil y persiste cada transición. OpenAPI en `/openapi.json` documenta el contrato `/api/v1`. Auditoría de implementación: 2026-10-11.

## Flujo

1. El usuario introduce un dominio o URL y confirma autorización; profundo requiere una segunda confirmación.
2. El backend valida sintaxis, conserva la entrada y extrae/normaliza el hostname IDNA.
3. Crea un registro UUID `queued`; una tarea del proceso lo pasa a `running`, valida sus resoluciones y ejecuta los módulos del perfil. Un destino bloqueado por DNS queda `failed` antes de contactar al objetivo.
4. Cada fuente devuelve evidencia normalizada o un error parcial; los proveedores opcionales ausentes no introducen penalización directa de reputación. Los fallbacks de otras comprobaciones tienen las limitaciones registradas en RISK-009.
5. El motor `2.0.0` calcula identidad/reputación (35 %), web/TLS (25 %), DNS/correo (20 %) y red (20 %). Normaliza los pesos sobre categorías disponibles; cobertura = módulos completados / módulos esperados del perfil. Confianza alta exige cobertura ≥85 % y algún proveedor disponible; media ≥60 %; baja en el resto.
6. Persiste informe JSON, score, riesgo, confianza, cobertura y duración. `GET /api/v1/scans/{id}/changes` calcula la comparación con el último informe completado anterior del mismo dominio; no persiste un diff independiente.
7. La UI puede reabrir, repetir, filtrar, comparar o borrar. La retención automática es de 90 días.

## Persistencia y recuperación

- `data/domaincheck.db`, fuera de Git, con SQLite WAL y transacciones cortas.
- Alembic mantiene el esquema; `python -m alembic upgrade head`, desde `backend/`, es obligatorio antes de una release. El arranque también crea tablas ausentes, pero no sustituye migraciones versionadas.
- Al iniciar, los trabajos `queued` y `running` se marcan `interrupted` y se eliminan filas vencidas por fecha de creación.
- La base no está cifrada; el alcance actual presupone un equipo local con acceso controlado.

## Decisiones de seguridad

- Se conserva la URL original solo como contexto; red, DNS y reputación reciben exclusivamente el hostname validado.
- Los redirects HTTP no se siguen. TLS/TCP usan la IP validada, pero HTTP usa el hostname y vuelve a resolver: queda pendiente fijar la conexión para prevenir DNS rebinding.
- Estándar limita puertos; profundo usa TCP completo y banners seguros con timeout y concurrencia acotados.
- No hay explotación, autenticación, búsqueda de secretos, crawling amplio, UDP ni evasión.
- La puntuación es heurística versionada y nunca una certificación de seguridad.

## Alcance real de la alpha

WHOIS usa `python-whois`, no RDAP. DNSSEC detecta DS/DNSKEY sin validar la cadena; MTA-STS/TLS-RPT consultan TXT, no la política HTTPS. Estándar consulta CT; profundo añade DNS de nombres comunes e indicios de CNAME colgante, no disponibilidad HTTP/TLS de cada subdominio. TLS profundo prueba versiones y muestra el cipher negociado, sin enumeración exhaustiva.

`SCAN_MAX_SECONDS` controla el bucle de puertos, no un timeout global. Un módulo terminado puede contener datos incompletos; cobertura no mide exhaustividad. Los detalles y defectos de scoring/redacción siguen en [riesgos conocidos](registers/KNOWN_RISKS.md).

## Evolución futura

Un despliegue compartido exige autenticación, autorización por alcance, cifrado o base gestionada, cola duradera, cancelación, auditoría y controles de cuota. Una auditoría web activa debe nacer como cambio OpenSpec separado.
