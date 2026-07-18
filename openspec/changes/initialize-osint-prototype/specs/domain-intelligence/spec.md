# Domain Intelligence Delta

## ADDED Requirements

### Requirement: Análisis OSINT inicial

El sistema SHALL recopilar WHOIS, DNS, TLS, HTTP, subdominios, IP, puertos y reputación opcional de un dominio público autorizado.

#### Scenario: Flujo completo

- GIVEN un dominio público y autorización confirmada
- WHEN se solicita el análisis completo
- THEN el sistema entrega un informe por secciones o identifica de forma explícita cada fuente parcial fallida
