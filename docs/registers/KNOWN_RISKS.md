# Riesgos conocidos y deuda

| ID | Riesgo | Prob. | Impacto | Mitigación actual | Próxima acción |
|---|---|---|---|---|---|
| RISK-001 | Exposición pública permitiría abusar del escáner. | Media | Alta | Bind local, confirmación, rate limit y bloqueo de IP privada. | Añadir autenticación, autorización y cola antes de desplegar. |
| RISK-002 | Port scan incompleto por firewall, CDN o timeout. | Alta | Media | Indicar IP analizada, duración y carácter orientativo. | Añadir cancelación, progreso real y estrategia multi-IP opcional. |
| RISK-003 | Datos WHOIS/CT/reputación incompletos o históricos. | Alta | Media | Informe parcial y fuentes identificadas. | Añadir timestamps, procedencia por campo y caché controlada. |
| RISK-004 | SQLite sin cifrar expone informes a quien acceda al equipo. | Media | Alta | Uso local, permisos del sistema y exclusión de Git. | Evaluar cifrado antes de compartir o desplegar. |
| RISK-005 | Heurística de score puede producir falsa confianza. | Media | Alta | Riesgo, score, cobertura y confianza separados; reglas y evidencias versionadas. | Calibrar contra casos de referencia y revisión experta. |
| RISK-006 | Un análisis profundo genera tráfico visible y puede agotar tiempo/sockets. | Media | Media | Segunda confirmación, timeout y concurrencia acotados. | Añadir cancelación y progreso de red granular. |
