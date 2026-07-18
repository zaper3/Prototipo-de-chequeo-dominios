import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.database import ScanRepository
from app.models import (
    DeleteAllRequest,
    DeleteResponse,
    HealthResponse,
    RiskLevel,
    ScanChanges,
    ScanHistoryPage,
    ScanJob,
    ScanProfile,
    ScanRequest,
    ScanStatus,
)
from app.security import UnsafeTargetError, normalize_target
from app.services.scanner import run_scan


settings = get_settings()
repository = ScanRepository(settings.database_url)
rate_buckets: dict[str, deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await repository.initialize()
    await repository.mark_interrupted()
    await repository.cleanup(settings.history_retention_days)
    yield
    await repository.close()


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="API local para análisis OSINT autorizado de dominios públicos.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def secure_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'"
    )
    return response


def enforce_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "local"
    now = time.monotonic()
    bucket = rate_buckets[client]
    while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_scans:
        raise HTTPException(
            status_code=429,
            detail="Límite temporal de análisis alcanzado. Inténtalo más tarde.",
        )
    bucket.append(now)


async def execute_scan(job_id: str, payload: ScanRequest) -> None:
    await repository.update_progress(
        job_id, ScanStatus.RUNNING, "Preparando análisis", 1
    )

    async def progress(stage: str, value: int) -> None:
        await repository.update_progress(job_id, ScanStatus.RUNNING, stage, value)

    try:
        report = await run_scan(
            payload.requested_target,
            payload.effective_profile,
            settings,
            progress,
        )
        await repository.complete(job_id, report)
        await repository.cleanup(settings.history_retention_days)
    except (ValueError, UnsafeTargetError) as exc:
        await repository.fail(job_id, str(exc))
    except asyncio.CancelledError:
        await repository.fail(
            job_id, "El análisis fue cancelado.", "Análisis cancelado"
        )
        raise
    except Exception:
        await repository.fail(
            job_id,
            "El análisis no pudo completarse por un error interno.",
        )


@app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.post(
    "/api/v1/scans",
    response_model=ScanJob,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["scans"],
)
async def create_scan(payload: ScanRequest, request: Request) -> ScanJob:
    enforce_rate_limit(request)
    try:
        target = normalize_target(payload.requested_target)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job = await repository.create_job(
        job_id=str(uuid4()),
        input_target=target.original,
        domain=target.domain,
        profile=payload.effective_profile,
        options={
            "profile": payload.effective_profile.value,
            "legacy_options": payload.options.model_dump(mode="json")
            if payload.options
            else None,
        },
    )
    asyncio.create_task(execute_scan(job.id, payload))
    return job


@app.get("/api/v1/scans", response_model=ScanHistoryPage, tags=["history"])
async def list_scans(
    query: str | None = None,
    risk_level: RiskLevel | None = None,
    profile: ScanProfile | None = None,
    scan_status: ScanStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ScanHistoryPage:
    return await repository.list(
        query=query,
        risk_level=risk_level,
        profile=profile,
        status=scan_status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@app.delete("/api/v1/scans", response_model=DeleteResponse, tags=["history"])
async def delete_all_scans(payload: DeleteAllRequest) -> DeleteResponse:
    return DeleteResponse(deleted=await repository.delete_all())


@app.get("/api/v1/scans/{job_id}", response_model=ScanJob, tags=["scans"])
async def get_scan(job_id: str) -> ScanJob:
    job = await repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return job


@app.get("/api/v1/scans/{job_id}/changes", response_model=ScanChanges, tags=["history"])
async def get_scan_changes(job_id: str) -> ScanChanges:
    changes = await repository.changes(job_id)
    if not changes:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return changes


@app.delete("/api/v1/scans/{job_id}", response_model=DeleteResponse, tags=["history"])
async def delete_scan(
    job_id: str, confirm: bool = Query(default=False)
) -> DeleteResponse:
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="La eliminación requiere confirm=true.",
        )
    deleted = await repository.delete_one(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return DeleteResponse(deleted=deleted)
