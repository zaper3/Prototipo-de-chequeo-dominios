## MODIFIED Requirements

### Requirement: Normalización segura del objetivo

El sistema SHALL aceptar dominios o URLs HTTP/HTTPS sin credenciales ni puerto explícito, conservar la entrada original, normalizar el hostname mediante IDNA y rechazar IP directas o cualquier resolución no global.

#### Scenario: URL pública válida

- GIVEN `https://ejemplo.com/ruta` y autorización confirmada
- WHEN todas las IP de `ejemplo.com` son públicas
- THEN crea un trabajo para `ejemplo.com` y no analiza la ruta

### Requirement: Perfiles de recopilación

El sistema SHALL ofrecer perfiles rápido, estándar y profundo, ejecutando únicamente los módulos y límites definidos para cada uno.

#### Scenario: Perfil profundo

- GIVEN autorización general y confirmación profunda explícitas
- WHEN alcanza la fase de red
- THEN permite TCP completo y controles ampliados sin explotación, UDP ni evasión
