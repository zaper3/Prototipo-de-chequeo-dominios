## ADDED Requirements

### Requirement: README bilingüe con evidencia visual honesta

El repositorio SHALL mantener README.md en español y README.en.md en inglés con hechos, comandos y límites equivalentes; las capturas SHALL identificar su procedencia y si contienen datos sintéticos.

#### Scenario: Galería con fixtures

- GIVEN capturas del frontend con una API simulada y datos ficticios
- WHEN se publican en ambos README
- THEN se etiquetan como demostración, sin afirmar escaneo real, traducción de la UI o validación del motor

### Requirement: Verificación de documentación visual

La entrega SHALL verificar enlaces/anchors, paridad de comandos y sincronía de medios; una actualización documental SHALL NOT cambiar versión, licencia o tags del producto sin autorización específica.

#### Scenario: Publicación documental

- GIVEN una mejora visual y bilingüe sin cambios del motor
- WHEN se prepara para la publicación autorizada
- THEN conserva versión y tag, comprueba procedencia de imágenes y usa PR con CI antes de fusionar
