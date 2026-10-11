# Prototipo de chequeo de dominios

Dashboard web local para analizar la exposición de un dominio público con señales OSINT, controles activos acotados e historial comparable. Acepta dominios o URLs HTTP/HTTPS, conserva la entrada y analiza únicamente el hostname normalizado.

> **Uso autorizado:** todos los perfiles generan tráfico hacia el objetivo, incluido rápido (TLS y HTTP). Úsalo solo sobre activos propios o con autorización expresa. La categoría indica riesgo observado, no demuestra que un sitio sea seguro.

## Estado

- Versión publicada: `0.2.0-alpha.1` ([SemVer 2.0.0](https://semver.org/)).
- Stack: React 19, TypeScript, Vite 8, FastAPI, SQLAlchemy asíncrono, Alembic y SQLite.
- Uso: aplicación local para un único usuario, sin autenticación ni despliegue público.
- Método: OpenSpec, CI DevOps y registros adaptados de cambios, incidentes y releases ITIL.

En este equipo, desde el **2026-10-11**, la copia de desarrollo canónica es:

`C:\Users\Usuario\Documents\Visual Studio Projects\Prototipo de chequeo dominios`

La copia anterior en OneDrive queda como respaldo retirado, no como entorno de trabajo. Abre [DomainCheck.code-workspace](DomainCheck.code-workspace) desde la nueva ubicación; los entornos virtuales deben recrearse al cambiar de ruta. Consulta la [auditoría de consolidación](docs/WORKSPACE_AUDIT_2026-10-11.md).

## Capacidades

- Perfiles **rápido**, **estándar** y **profundo**, con estimación y confirmación específica del escaneo completo.
- WHOIS e identidad; DNS/CAA y señales básicas de DNSSEC/correo; TLS, HTTP, cookies/CORS, CT logs, subdominios e IP. RDAP no está implementado.
- Red: puertos principales en estándar; TCP `1–65535`, banners seguros y controles ampliados en profundo.
- Enriquecimientos opcionales: Google Safe Browsing, VirusTotal, SecurityTrails y MDN Observatory.
- Riesgo `Bajo`, `Moderado`, `Alto`, `Crítico` o `Datos insuficientes`, separado de score, cobertura y confianza.
- Hallazgos trazables con evidencia, fuente, impacto, recomendación y referencia.
- Informes completos en SQLite durante 90 días: búsqueda, filtros, reapertura, repetición, comparación y borrado.
- Bloqueo de IP directas y resoluciones privadas, locales o reservadas.

El perfil profundo no busca secretos, backups o paneles; tampoco explota, autentica, inyecta, evade, hace crawling extensivo ni escanea UDP.

## Instalación

Requiere Python 3.12+, Node.js 24+ y npm 11+. Entorno local verificado el 2026-10-11: Python 3.13.15, Node.js 24.14.0 y npm 11.9.0. Ejecuta los comandos desde la raíz del checkout elegido, no desde la copia retirada.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

En otra terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Abre `http://127.0.0.1:5173`; Vite envía `/api` a `127.0.0.1:8000`. API y OpenAPI quedan en `http://127.0.0.1:8000` y `http://127.0.0.1:8000/docs`. Para clientes que llamen directamente a la API, configura su origen en `FRONTEND_ORIGINS`.

## Datos y configuración

La base se crea en `data/domaincheck.db` y queda excluida de Git. SQLite usa WAL; al arrancar se recuperan trabajos interrumpidos y se purgan informes que superen `HISTORY_RETENTION_DAYS` (90 de forma predeterminada).

Las claves externas de `.env` son opcionales. Su ausencia no aplica una penalización de score de reputación y puede reducir cobertura/confianza. La cobertura actual cuenta módulos, no porcentaje de puertos ni exhaustividad de las fuentes. Consulta `.env.example` para límites de red, retención e integraciones. Ejecuta el backend y Alembic desde `backend/`: la ruta SQLite predeterminada es relativa a ese directorio.

## Calidad

```powershell
cd backend
python -m ruff check app tests migrations
python -m ruff format --check app tests migrations
python -m pytest
python -m alembic upgrade head

cd ..\frontend
npm test -- --run
npm run build

cd ..
node scripts/check-docs.mjs
python -m unittest discover -s scripts/tests
python -m ruff check scripts
python -m ruff format --check scripts
npx -y @fission-ai/openspec@1.14.1 validate --all --no-interactive
```

Las pruebas automatizadas mockean las fuentes externas y no escanean dominios públicos.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Operación, DevOps e ITIL](docs/OPERATIONS.md)
- [Versiones y candidatas](docs/RELEASE_MANAGEMENT.md)
- [Riesgos y limitaciones pendientes](docs/registers/KNOWN_RISKS.md)
- [Auditoría de ubicaciones y validación actual](docs/WORKSPACE_AUDIT_2026-10-11.md)
- [Cambio OpenSpec 0.2.0](openspec/changes/add-history-and-risk-engine/)
- [Seguridad](SECURITY.md) y [changelog](CHANGELOG.md)

## Limitaciones

El resultado depende de la disponibilidad y actualidad de fuentes públicas y no sustituye una auditoría profesional. WHOIS puede estar oculto, CT puede incluir nombres históricos, un firewall altera la visibilidad de puertos y una sola IP puede no representar toda una CDN. El profundo prueba protocolos TLS, pero no enumera todos los cifrados ni comprueba HTTP/TLS de cada subdominio. SQLite no está cifrado y su protección depende del acceso local al equipo. Las limitaciones de SSRF, scoring y dependencias están registradas en [riesgos conocidos](docs/registers/KNOWN_RISKS.md); no se promete protección completa.
