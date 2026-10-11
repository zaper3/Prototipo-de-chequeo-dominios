## MODIFIED Requirements

### Requirement: Evaluación versionada por categorías

El sistema SHALL producir score, riesgo, confianza, cobertura, subpuntuaciones 35/25/20/20 y versión de reglas, sin describir el resultado como certificación.

#### Scenario: Clasificación por score y hallazgos

- GIVEN cobertura de al menos 50 %
- WHEN finaliza la evaluación
- THEN clasifica Bajo 85–100, Moderado 65–84, Alto 40–64 o Crítico menor de 40, permitiendo que hallazgos medios, altos, críticos o amenazas confirmadas eleven la categoría

#### Scenario: Cobertura insuficiente

- GIVEN cobertura menor de 50 %
- WHEN finaliza el análisis
- THEN clasifica como Datos insuficientes

### Requirement: Hallazgos trazables

Cada hallazgo SHALL incluir ID estable, categoría, evidencia, fuente, impacto de score, recomendación y referencia.

#### Scenario: Presentación del resultado

- GIVEN un informe completado
- WHEN se presenta
- THEN explica la categoría, hasta tres prioridades disponibles y limitaciones
