# Proposal: Initialize OSINT domain-check prototype

> Registro histórico de la candidata local 0.1, sustituida por `add-history-and-risk-engine`. Su exclusión de persistencia no describe la alpha actual. Estado reconciliado el 2026-10-11; no hubo release/tag 0.1 publicado.

## Why

El repositorio solo contenía una descripción inicial y necesitaba una base funcional, segura y documentada para analizar dominios desde una interfaz local.

## What Changes

- Crear frontend React y backend FastAPI con API asíncrona.
- Incorporar recopilación solicitada, escaneo TCP completo opcional y evaluación básica.
- Añadir salvaguardas de autorización, SSRF, frecuencia, tiempo y concurrencia.
- Establecer OpenSpec, SemVer, registros ITIL y CI DevOps.

## Out of Scope

Despliegue público, autenticación, persistencia, explotación, fuerza bruta extensa, UDP y garantía de auditoría.

## Operational Risk and Rollback

El tráfico activo puede ser interpretado como escaneo; la mitigación es uso local autorizado y límites configurables. Reversión: volver al commit inicial, ya que no existen datos persistentes ni migraciones.
