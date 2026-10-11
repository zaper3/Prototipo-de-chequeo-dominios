# Design

## Persistence

SQLAlchemy asíncrono usa SQLite WAL y transacciones cortas. Un registro conserva entrada, hostname, perfil, opciones, estado, tiempos, score, riesgo, confianza, reglas, informe JSON y errores. Alembic crea el esquema. Al arrancar se marcan trabajos interrumpidos y se aplica retención.

## Collection profiles

El orquestador selecciona módulos declarativos. Rápido cubre identidad WHOIS, DNS principal, TLS, HTTP y reputación disponible. Estándar añade señales de correo/DNSSEC, CT, subdominios y puertos acotados. Profundo añade TCP completo, banners seguros, protocolos TLS, DNS/CNAME de subdominios y contenido inicial limitado. No hay RDAP, enumeración exhaustiva de cifrados ni disponibilidad HTTP/TLS de subdominios; estas ampliaciones del plan siguen pendientes.

## Risk model

El motor puro `2.0.0` agrega cuatro categorías 35/25/20/20 normalizando sobre pesos disponibles. La categoría se deriva de score, severidad máxima y amenazas confirmadas, salvo cobertura menor del 50 % que prima como Datos insuficientes. Cobertura por módulos y confianza son dimensiones independientes; proveedores no configurados no aplican penalización de reputación. IDs y evidencias permiten comparación estable.

## Threat controls

La normalización nunca convierte una ruta en objetivo. Se bloquean credenciales, puertos explícitos, IP directas y resoluciones iniciales no globales. La respuesta HTTP raíz se limita en tamaño; la lectura de security.txt aún no tiene ese límite. Los puertos tienen plazo/concurrencia y los errores externos se aíslan. HTTP vuelve a resolver el hostname y los errores no garantizan redacción de claves: ver [riesgos conocidos](../../../docs/registers/KNOWN_RISKS.md), revisados el 2026-10-11.

## Verification

Pruebas sin red pública cubren normalización, SSRF, persistencia, retención, reinicio, CRUD, comparación, perfiles y fronteras del motor. Ruff, pytest, Vitest, build, Alembic y OpenSpec conforman el gate; el smoke real exige objetivo autorizado.
