# Dashboard Specification

## Purpose

Presentar análisis actuales e históricos de forma moderna, responsive, accesible y comprensible.

## Requirements

### Requirement: Inicio informado y autorizado

La interfaz SHALL aceptar dominio o URL, anticipar el hostname que se analizará, requerir autorización, mostrar alcance/duración de cada perfil y pedir confirmación adicional para profundo.

#### Scenario: URL completa

- GIVEN `https://ejemplo.com/ruta` escrito
- WHEN el hostname puede normalizarse
- THEN muestra que analizará `ejemplo.com` y que la ruta queda fuera

### Requirement: Riesgo multidimensional

La interfaz SHALL presentar categoría de riesgo, score, confianza, cobertura y subpuntuaciones como conceptos separados, con secciones de reputación, identidad, DNS/correo, TLS, web, subdominios, red y evidencias.

#### Scenario: Informe parcial

- GIVEN fuentes opcionales ausentes
- WHEN se abre el informe
- THEN se muestran cobertura/confianza reducidas, limitaciones y evidencia disponible

### Requirement: Historial gestionable

La interfaz SHALL permitir buscar, filtrar, paginar, abrir, repetir, eliminar y comparar informes persistidos.

#### Scenario: Reapertura

- GIVEN un informe de los últimos 90 días
- WHEN el usuario lo selecciona
- THEN recupera el informe completo sin volver a escanear y presenta sus cambios frente al anterior
