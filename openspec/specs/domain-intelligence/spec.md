# Domain Intelligence Specification

## Purpose

Definir la recopilación autorizada, perfilada y tolerante a fallos de señales públicas de un dominio.

## Requirements

### Requirement: Normalización segura del objetivo

El sistema SHALL aceptar dominios o URLs HTTP/HTTPS sin credenciales ni puerto explícito, conservar la entrada original, normalizar el hostname mediante IDNA y rechazar IP directas o cualquier resolución no global.

#### Scenario: URL pública válida

- GIVEN `https://ejemplo.com/ruta` y autorización confirmada
- WHEN todas las IP de `ejemplo.com` son públicas
- THEN crea un trabajo para `ejemplo.com` y no analiza la ruta

#### Scenario: Objetivo inseguro

- GIVEN credenciales, esquema no permitido, IP directa o resolución privada, local o reservada
- WHEN se solicita el análisis
- THEN rechaza el objetivo antes de efectuar comprobaciones activas

### Requirement: Perfiles de recopilación

El sistema SHALL ofrecer perfiles rápido, estándar y profundo, y SHALL ejecutar únicamente los módulos y límites definidos para el perfil elegido.

#### Scenario: Perfil estándar predeterminado

- GIVEN una solicitud sin perfil explícito
- WHEN comienza la recopilación
- THEN usa estándar y no recorre TCP `1–65535`

#### Scenario: Perfil profundo

- GIVEN autorización general y confirmación profunda explícitas
- WHEN alcanza la fase de red
- THEN permite TCP `1–65535`, banners seguros y comprobaciones ampliadas sin explotación, UDP, autenticación ni evasión

### Requirement: Recopilación tolerante a fallos

El sistema SHALL recopilar identidad, DNS/correo, TLS, HTTP, CT/subdominios y red según el perfil, y MAY enriquecer con Google Safe Browsing, VirusTotal, SecurityTrails y MDN Observatory.

#### Scenario: Proveedor ausente

- GIVEN una integración sin clave o no disponible
- WHEN finalizan los módulos restantes
- THEN conserva resultados, registra la omisión y no penaliza el score
