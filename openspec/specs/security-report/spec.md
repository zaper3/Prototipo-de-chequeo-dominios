# Security Report Specification

## Purpose

Convertir evidencias heterogéneas en un resultado comprensible y trazable sin presentarlo como certificación.

## Requirements

### Requirement: Evaluación versionada por categorías

El sistema SHALL calcular score `0–100` y subpuntuaciones de identidad/reputación 35 %, web/TLS 25 %, DNS/correo 20 % y red 20 %, y SHALL publicar la versión de reglas.

#### Scenario: Clasificación por score y hallazgos

- GIVEN cobertura de al menos 50 %
- WHEN finaliza la evaluación
- THEN clasifica Bajo 85–100, Moderado 65–84, Alto 40–64 o Crítico menor de 40, permitiendo que hallazgos medios, altos, críticos o amenazas confirmadas eleven la categoría

#### Scenario: Cobertura insuficiente

- GIVEN cobertura menor de 50 %
- WHEN se prepara el resumen
- THEN la categoría es Datos insuficientes sin afirmar seguridad

### Requirement: Confianza independiente del score

El sistema SHALL mostrar confianza Alta, Media o Baja según cobertura y disponibilidad externa; la ausencia de un proveedor SHALL reducir cobertura/confianza sin restar score.

#### Scenario: Inteligencia externa no configurada

- GIVEN que no hay claves de reputación
- WHEN las comprobaciones locales concluyen
- THEN el score refleja solo evidencia disponible y la confianza comunica la limitación

### Requirement: Hallazgos trazables

Cada hallazgo SHALL incluir ID estable, categoría, severidad, evidencia, fuente, impacto de score, recomendación y referencia técnica.

#### Scenario: Presentación del resultado

- GIVEN un informe completado
- WHEN se abre el resumen
- THEN explica por qué obtuvo la categoría, muestra hasta tres acciones prioritarias disponibles y enumera limitaciones y errores parciales
