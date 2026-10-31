# Delivery Governance Specification

## Purpose

Mantener workspace, datos y documentación verificables durante consolidaciones locales y sincronizaciones autorizadas. El historial de aceptación de octubre de 2026 consta en el cambio archivado y en la auditoría del workspace.

## Requirements

### Requirement: Consolidación no destructiva del workspace

El proceso SHALL contrastar copias y GitHub antes de establecer un checkout canónico y SHALL preservar cambios locales, configuración e historial sin eliminar la copia retirada.

#### Scenario: Copia destino incompleta

- GIVEN copias con el mismo HEAD y cuatro archivos tracked ausentes en destino
- WHEN los restantes archivos y SQLite coinciden y se han respaldado ambas
- THEN restaura los archivos desde origen y verifica hashes sin perder datos

### Requirement: Trazabilidad documental y de publicación

El proyecto SHALL verificar versiones/enlaces/especificaciones y registrar evidencia y límites; una sincronización documental SHALL NOT mover tags publicados ni afirmar gates no ejecutados.

#### Scenario: Consolidación de la alpha

- GIVEN la release alpha publicada y aprobación de sincronización
- WHEN pasan los gates locales y CI de la PR
- THEN sincroniza master y conserva el tag alpha sobre su commit original

### Requirement: Respaldo SQLite consistente

El helper SHALL incluir transacciones WAL confirmadas, rechazar sobrescritura y verificar integridad y cantidad de registros.

#### Scenario: WAL contiene datos confirmados

- GIVEN una base con registros confirmados aún en WAL
- WHEN se crea un respaldo nuevo
- THEN el respaldo contiene los registros y la fuente permanece sin cambios lógicos

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
