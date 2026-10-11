## ADDED Requirements

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
