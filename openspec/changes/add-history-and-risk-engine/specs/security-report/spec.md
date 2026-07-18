## MODIFIED Requirements

### Requirement: Evaluación versionada por categorías

El sistema SHALL producir score, riesgo, confianza, cobertura, subpuntuaciones 35/25/20/20 y versión de reglas, sin describir el resultado como certificación.

#### Scenario: Cobertura insuficiente

- GIVEN cobertura menor de 50 %
- WHEN finaliza el análisis
- THEN clasifica como Datos insuficientes

### Requirement: Hallazgos trazables

Cada hallazgo SHALL incluir ID estable, categoría, evidencia, fuente, impacto de score, recomendación y referencia.

#### Scenario: Resumen explicativo

- GIVEN un informe completado
- WHEN se presenta
- THEN explica la categoría, tres prioridades y limitaciones
