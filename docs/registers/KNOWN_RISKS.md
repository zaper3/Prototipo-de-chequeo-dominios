# Riesgos conocidos y deuda

Revisión: 2026-10-11. Deuda identificada, no aprobación automática para desplegar ni aceptación de riesgos altos de una nueva candidata.

| ID | Riesgo | Prob. | Impacto | Mitigación actual | Próxima acción |
|---|---|---|---|---|---|
| RISK-001 | Exposición pública permitiría abusar del escáner. | Media | Alta | Bind local, confirmación, rate limit y bloqueo de IP privada. | Añadir autenticación, autorización y cola antes de desplegar. |
| RISK-002 | Port scan incompleto por firewall, CDN o timeout. | Alta | Media | Indicar IP analizada, duración y carácter orientativo. | Añadir cancelación, progreso real y estrategia multi-IP opcional. |
| RISK-003 | Datos WHOIS/CT/reputación incompletos o históricos. | Alta | Media | Informe parcial y fuentes identificadas. | Añadir timestamps, procedencia por campo y caché controlada. |
| RISK-004 | SQLite sin cifrar expone informes a quien acceda al equipo. | Media | Alta | Uso local, permisos del sistema y exclusión de Git. | Evaluar cifrado antes de compartir o desplegar. |
| RISK-005 | Heurística de score puede producir falsa confianza. | Media | Alta | Riesgo, score, cobertura y confianza separados; reglas y evidencias versionadas. | Calibrar contra casos de referencia y revisión experta. |
| RISK-006 | Un análisis profundo genera tráfico visible y puede agotar tiempo/sockets. | Media | Media | Segunda confirmación, timeout y concurrencia acotados. | Añadir cancelación y progreso de red granular. |
| RISK-007 | DNS rebinding en HTTP: nueva resolución al conectar puede diferir de la validación inicial. | Media | Alta | Uso estrictamente local/autorizado, sin redirects; TLS/TCP fijan IP. | BUG-2026-008: fijar/revalidar conexión HTTP y probar respuestas DNS cambiantes. |
| RISK-008 | Errores de proveedores pueden incluir URLs con claves; informes también conservan URL original/cookies. | Media | Alta | Sin claves configuradas en la migración; no compartir informes/logs, evitar tokens en URLs. | BUG-2026-009: redacción de secretos y minimización de datos con regresión. |
| RISK-009 | Ausencia de controles no distingue siempre datos omitidos/fallidos: rápido no recoge correo/DNSSEC; fallback TLS marca invalid. | Alta | Media | Categoría orientativa y errores/cobertura visibles; no afirmar seguridad. | BUG-2026-010: estados observados/ausentes/no comprobados y recalibración versionada. |
| RISK-010 | Lock del frontend con 6 paquetes afectados: @vitest/mocker, vitest, nanoid, postcss, source-map-js, undici. | Media | Alta | Alertas de tooling dev; npm audit --omit=dev sin alertas en esta fecha; no exponer servidores de desarrollo ni procesar entradas no confiables. | BUG-2026-007: cambio OpenSpec de dependencias, pruebas y nuevo gate de release. |
| RISK-011 | Cobertura por módulos sobreestima exhaustividad; puertos pueden terminar por plazo y aun contar network como completo; WHOIS no tiene deadline global. | Alta | Media | Documentar límite de puertos y cobertura no exhaustiva; no usar porcentajes como garantía. | Timeout global, métricas de puertos intentados/completos y límites de tareas/banners. |
| RISK-012 | Diferencias entre alcance previsto y alpha: sin RDAP, enumeración total de cifrados ni disponibilidad HTTP/TLS de subdominios. | Alta | Media | README/arquitectura precisan alcance; CNAME colgante es indicio, no takeover confirmado. | Implementar cada ampliación en cambio separado; corregir etiqueta histórica WHOIS/RDAP del motor. |

DNSSEC solo detecta DS/DNSKEY (no valida criptografía); MTA-STS y TLS-RPT solo TXT (no política HTTPS). La lista no es una auditoría exhaustiva ni un pentest.

La auditoría npm de 2026-10-11 registró 3 alertas altas y 3 moderadas en paquetes de desarrollo, no seis pruebas de explotación. Referencias de origen: [Vitest](https://github.com/advisories/GHSA-82fw-gwwq-j7x9), [nanoid](https://github.com/advisories/GHSA-2v37-7h3g-55p8), [PostCSS](https://github.com/advisories/GHSA-fxqj-rqcc-2cmp), [source-map-js](https://github.com/advisories/GHSA-68fv-2mgg-jv7q), [Undici](https://github.com/advisories/GHSA-w293-vg96-wgc3). Deben reconsultarse al preparar el fix.
