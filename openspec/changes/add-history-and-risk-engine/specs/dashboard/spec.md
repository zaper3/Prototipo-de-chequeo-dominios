## ADDED Requirements

### Requirement: Historial persistente

La interfaz SHALL permitir buscar, filtrar, paginar, abrir, repetir, comparar y borrar informes conservados durante 90 días.

#### Scenario: Abrir informe anterior

- GIVEN un análisis persistido
- WHEN el usuario lo abre
- THEN presenta el informe y su comparación sin repetir tráfico

### Requirement: Inicio perfilado

La interfaz SHALL anticipar el hostname de una URL y mostrar alcance/duración de los perfiles, requiriendo confirmación adicional para profundo.

#### Scenario: URL completa

- GIVEN una URL HTTP/HTTPS
- WHEN se reconoce su hostname
- THEN informa qué dominio se analizará y excluye la ruta
