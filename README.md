# Prototipo de chequeo de dominios

Dashboard web local para analizar la exposición de un dominio público con señales OSINT, controles activos acotados e historial comparable. Acepta dominios o URLs HTTP/HTTPS, conserva la entrada y analiza únicamente el hostname normalizado.

> **Uso autorizado:** los perfiles estándar y profundo generan tráfico hacia el objetivo. Úsalo solo sobre activos propios o con autorización expresa. La categoría indica riesgo observado, no demuestra que un sitio sea seguro.

## Estado

- Versión publicada: `0.2.0-alpha.1` ([SemVer 2.0.0](https://semver.org/)).
- Stack: React 19, TypeScript, Vite 8, FastAPI, SQLAlchemy asíncrono, Alembic y SQLite.
- Uso: aplicación local para un único usuario, sin autenticación ni despliegue público.
- Método: OpenSpec, CI DevOps y registros adaptados de cambios, incidentes y releases ITIL.

## Capacidades

- Perfiles **rápido**, **estándar** y **profundo**, con estimación y confirmación específica del escaneo completo.
- WHOIS/RDAP, identidad, DNS, correo, DNSSEC, CAA, TLS, HTTP, cookies/CORS, CT logs, subdominios e IP.
- Red: puertos principales en estándar; TCP `1–65535`, banners seguros y controles ampliados en profundo.
- Enriquecimientos opcionales: Google Safe Browsing, VirusTotal, SecurityTrails y MDN Observatory.
- Riesgo `Bajo`, `Moderado`, `Alto`, `Crítico` o `Datos insuficientes`, separado de score, cobertura y confianza.
- Hallazgos trazables con evidencia, fuente, impacto, recomendación y referencia.
- Informes completos en SQLite durante 90 días: búsqueda, filtros, reapertura, repetición, comparación y borrado.
- Bloqueo de IP directas y resoluciones privadas, locales o reservadas.

El perfil profundo no busca secretos, backups o paneles; tampoco explota, autentica, inyecta, evade, hace crawling extensivo ni escanea UDP.

## Instalación

Requiere Python 3.12+, Node.js 24+ y npm 11+.

```powershell
Copy-Item .env.example .env

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`; API y OpenAPI quedan en `http://127.0.0.1:8000` y `http://127.0.0.1:8000/docs`.

## Datos y configuración

La base se crea en `data/domaincheck.db` y queda excluida de Git. SQLite usa WAL; al arrancar se recuperan trabajos interrumpidos y se purgan informes que superen `HISTORY_RETENTION_DAYS` (90 de forma predeterminada).

Las claves externas de `.env` son opcionales. Su ausencia reduce cobertura/confianza, nunca el score. Consulta `.env.example` para límites de red, retención e integraciones.

## Calidad

```powershell
cd backend
ruff check app tests migrations
ruff format --check app tests migrations
pytest
python -m alembic upgrade head

cd ..\frontend
npm test -- --run
npm run build

cd ..
npx -y @fission-ai/openspec@latest validate --all --no-interactive
```

Las pruebas automatizadas mockean las fuentes externas y no escanean dominios públicos.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Operación, DevOps e ITIL](docs/OPERATIONS.md)
- [Versiones y candidatas](docs/RELEASE_MANAGEMENT.md)
- [Cambio OpenSpec 0.2.0](openspec/changes/add-history-and-risk-engine/)
- [Seguridad](SECURITY.md) y [changelog](CHANGELOG.md)

## Limitaciones

El resultado depende de la disponibilidad y actualidad de fuentes públicas y no sustituye una auditoría profesional. WHOIS puede estar oculto, CT puede incluir nombres históricos, un firewall altera la visibilidad de puertos y una sola IP puede no representar toda una CDN. SQLite no está cifrado en esta fase y su protección depende del acceso local al equipo.
