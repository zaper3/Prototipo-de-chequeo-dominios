# Design

## Persistence

SQLAlchemy asíncrono usa SQLite WAL y transacciones cortas. Un registro conserva entrada, hostname, perfil, opciones, estado, tiempos, score, riesgo, confianza, reglas, informe JSON y errores. Alembic crea el esquema. Al arrancar se marcan trabajos interrumpidos y se aplica retención.

## Collection profiles

El orquestador selecciona módulos declarativos. Rápido cubre identidad, DNS principal, TLS, HTTP y reputación disponible. Estándar añade correo/DNSSEC, CT, subdominios y puertos acotados. Profundo añade TCP completo, banners seguros, protocolos TLS, disponibilidad de subdominios y contenido inicial limitado.

## Risk model

El motor puro `2.0.0` agrega cuatro categorías 35/25/20/20. La categoría se deriva de score, severidad máxima y amenazas confirmadas. Cobertura y confianza son dimensiones independientes; proveedores no configurados no descuentan score. IDs y evidencias permiten comparación estable.

## Threat controls

La normalización nunca convierte una ruta en objetivo. Se bloquean credenciales, puertos, IP directas y cualquier resolución no global. HTTP se limita en tamaño, red en tiempo/concurrencia y los errores externos se aíslan. Los informes no contienen claves de proveedor.

## Verification

Pruebas sin red pública cubren normalización, SSRF, persistencia, retención, reinicio, CRUD, comparación, perfiles y fronteras del motor. Ruff, pytest, Vitest, build, Alembic y OpenSpec conforman el gate; el smoke real exige objetivo autorizado.
