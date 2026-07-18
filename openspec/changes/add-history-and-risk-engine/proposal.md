# Proposal: Add history and risk engine

## Why

La candidata inicial perdía resultados al reiniciar, exigía un dominio desnudo y resumía la seguridad en un score sin expresar cobertura ni confianza. Eso impedía seguir la evolución y podía crear falsa certeza.

## What Changes

- Persistir trabajos e informes 90 días en SQLite con historial, comparación y borrado.
- Aceptar dominios y URLs HTTP/HTTPS analizando solo el hostname público normalizado.
- Introducir perfiles rápido, estándar y profundo con límites y autorización explícitos.
- Reemplazar la lectura absoluta por riesgo, confianza, cobertura y subpuntuaciones versionadas.
- Ampliar evidencia y enriquecimientos opcionales.

## Out of Scope

Autenticación, despliegue público, cifrado de la base, UDP, crawling extensivo, secretos, explotación, inyecciones, credenciales, evasión y auditoría web activa.

## Operational Risk and Rollback

El perfil profundo puede generar tráfico visible y SQLite añade riesgo de retención local. Se mitiga con doble confirmación, límites, retención y exclusión de Git. Para revertir: detener servicios, respaldar la base y volver al tag anterior; no aplicar downgrade destructivo sin una copia verificada.
