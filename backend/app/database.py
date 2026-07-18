from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    delete,
    func,
    select,
    update,
)
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models import (
    ConfidenceLevel,
    RiskLevel,
    ScanChanges,
    ScanHistoryItem,
    ScanHistoryPage,
    ScanJob,
    ScanProfile,
    ScanReport,
    ScanStatus,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    input_target: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(253), nullable=False, index=True)
    profile: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(160), nullable=False, default="En cola")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    score: Mapped[int | None] = mapped_column(Integer)
    risk_level: Mapped[str | None] = mapped_column(String(16), index=True)
    confidence: Mapped[str | None] = mapped_column(String(16))
    coverage_percent: Mapped[float | None] = mapped_column(Float)
    ruleset_version: Mapped[str | None] = mapped_column(String(24))
    options_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    report_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=timezone.utc)


def record_to_job(record: ScanRecord) -> ScanJob:
    report = (
        ScanReport.model_validate(record.report_json) if record.report_json else None
    )
    return ScanJob(
        id=record.id,
        input_target=record.input_target,
        domain=record.domain,
        profile=ScanProfile(record.profile),
        status=ScanStatus(record.status),
        stage=record.stage,
        progress=record.progress,
        created_at=_as_utc(record.created_at) or utcnow(),
        updated_at=_as_utc(record.updated_at) or utcnow(),
        completed_at=_as_utc(record.completed_at),
        report=report,
        error=record.error,
    )


def record_to_history(record: ScanRecord) -> ScanHistoryItem:
    return ScanHistoryItem(
        id=record.id,
        input_target=record.input_target,
        domain=record.domain,
        profile=ScanProfile(record.profile),
        status=ScanStatus(record.status),
        created_at=_as_utc(record.created_at) or utcnow(),
        completed_at=_as_utc(record.completed_at),
        duration_seconds=record.duration_seconds,
        score=record.score,
        risk_level=RiskLevel(record.risk_level) if record.risk_level else None,
        confidence=ConfidenceLevel(record.confidence) if record.confidence else None,
        coverage_percent=record.coverage_percent,
        error=record.error,
    )


class ScanRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine: AsyncEngine = create_async_engine(database_url, pool_pre_ping=True)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def initialize(self) -> None:
        url = make_url(self.database_url)
        if url.get_backend_name() == "sqlite" and url.database not in {
            None,
            ":memory:",
        }:
            Path(url.database).resolve().parent.mkdir(parents=True, exist_ok=True)
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            if url.get_backend_name() == "sqlite":
                await connection.exec_driver_sql("PRAGMA journal_mode=WAL")
                await connection.exec_driver_sql("PRAGMA foreign_keys=ON")

    async def close(self) -> None:
        await self.engine.dispose()

    async def create_job(
        self,
        *,
        job_id: str,
        input_target: str,
        domain: str,
        profile: ScanProfile,
        options: dict[str, Any],
    ) -> ScanJob:
        now = utcnow()
        record = ScanRecord(
            id=job_id,
            input_target=input_target,
            domain=domain,
            profile=profile.value,
            status=ScanStatus.QUEUED.value,
            stage="En cola",
            progress=0,
            created_at=now,
            updated_at=now,
            options_json=options,
        )
        async with self.sessions() as session:
            session.add(record)
            await session.commit()
            return record_to_job(record)

    async def update_progress(
        self, job_id: str, status: ScanStatus, stage: str, progress: int
    ) -> None:
        async with self.sessions() as session:
            await session.execute(
                update(ScanRecord)
                .where(ScanRecord.id == job_id)
                .values(
                    status=status.value,
                    stage=stage,
                    progress=progress,
                    updated_at=utcnow(),
                )
            )
            await session.commit()

    async def complete(self, job_id: str, report: ScanReport) -> None:
        completed_at = utcnow()
        async with self.sessions() as session:
            await session.execute(
                update(ScanRecord)
                .where(ScanRecord.id == job_id)
                .values(
                    domain=report.domain,
                    status=ScanStatus.COMPLETED.value,
                    stage="Informe completado",
                    progress=100,
                    updated_at=completed_at,
                    completed_at=completed_at,
                    duration_seconds=report.duration_seconds,
                    score=report.score,
                    risk_level=report.risk_level.value,
                    confidence=report.confidence.value,
                    coverage_percent=report.coverage_percent,
                    ruleset_version=report.ruleset_version,
                    report_json=report.model_dump(mode="json"),
                    error=None,
                )
            )
            await session.commit()

    async def fail(
        self, job_id: str, error: str, stage: str = "Análisis fallido"
    ) -> None:
        now = utcnow()
        async with self.sessions() as session:
            await session.execute(
                update(ScanRecord)
                .where(ScanRecord.id == job_id)
                .values(
                    status=ScanStatus.FAILED.value,
                    stage=stage,
                    updated_at=now,
                    completed_at=now,
                    error=error,
                )
            )
            await session.commit()

    async def get(self, job_id: str) -> ScanJob | None:
        async with self.sessions() as session:
            record = await session.get(ScanRecord, job_id)
            return record_to_job(record) if record else None

    async def list(
        self,
        *,
        query: str | None = None,
        risk_level: RiskLevel | None = None,
        profile: ScanProfile | None = None,
        status: ScanStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ScanHistoryPage:
        filters = []
        if query:
            filters.append(func.lower(ScanRecord.domain).like(f"%{query.lower()}%"))
        if risk_level:
            filters.append(ScanRecord.risk_level == risk_level.value)
        if profile:
            filters.append(ScanRecord.profile == profile.value)
        if status:
            filters.append(ScanRecord.status == status.value)
        if date_from:
            filters.append(ScanRecord.created_at >= date_from)
        if date_to:
            filters.append(ScanRecord.created_at <= date_to)

        async with self.sessions() as session:
            total = await session.scalar(
                select(func.count()).select_from(ScanRecord).where(*filters)
            )
            result = await session.scalars(
                select(ScanRecord)
                .where(*filters)
                .order_by(ScanRecord.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            records: Sequence[ScanRecord] = result.all()
            return ScanHistoryPage(
                items=[record_to_history(record) for record in records],
                total=int(total or 0),
                limit=limit,
                offset=offset,
            )

    async def delete_one(self, job_id: str) -> int:
        async with self.sessions() as session:
            result = await session.execute(
                delete(ScanRecord).where(ScanRecord.id == job_id)
            )
            await session.commit()
            return int(result.rowcount or 0)

    async def delete_all(self) -> int:
        async with self.sessions() as session:
            result = await session.execute(delete(ScanRecord))
            await session.commit()
            return int(result.rowcount or 0)

    async def cleanup(self, retention_days: int) -> int:
        if retention_days <= 0:
            return 0
        cutoff = utcnow() - timedelta(days=retention_days)
        async with self.sessions() as session:
            result = await session.execute(
                delete(ScanRecord).where(ScanRecord.created_at < cutoff)
            )
            await session.commit()
            return int(result.rowcount or 0)

    async def mark_interrupted(self) -> int:
        now = utcnow()
        async with self.sessions() as session:
            result = await session.execute(
                update(ScanRecord)
                .where(
                    ScanRecord.status.in_(
                        [ScanStatus.QUEUED.value, ScanStatus.RUNNING.value]
                    )
                )
                .values(
                    status=ScanStatus.INTERRUPTED.value,
                    stage="Interrumpido por reinicio",
                    updated_at=now,
                    completed_at=now,
                    error="El análisis fue interrumpido al reiniciarse el servicio.",
                )
            )
            await session.commit()
            return int(result.rowcount or 0)

    async def changes(self, job_id: str) -> ScanChanges | None:
        async with self.sessions() as session:
            current = await session.get(ScanRecord, job_id)
            if not current:
                return None
            previous = await session.scalar(
                select(ScanRecord)
                .where(
                    ScanRecord.domain == current.domain,
                    ScanRecord.status == ScanStatus.COMPLETED.value,
                    ScanRecord.created_at < current.created_at,
                )
                .order_by(ScanRecord.created_at.desc())
                .limit(1)
            )
        result = ScanChanges(scan_id=job_id)
        if not previous or not current.report_json or not previous.report_json:
            return result

        current_report = ScanReport.model_validate(current.report_json)
        previous_report = ScanReport.model_validate(previous.report_json)
        current_findings = {finding.id for finding in current_report.findings}
        previous_findings = {finding.id for finding in previous_report.findings}
        current_ports = {int(port["port"]) for port in current_report.ports}
        previous_ports = {int(port["port"]) for port in previous_report.ports}
        current_subdomains = {item["name"] for item in current_report.subdomains}
        previous_subdomains = {item["name"] for item in previous_report.subdomains}
        current_serial = current_report.ssl.get("serial_number")
        previous_serial = previous_report.ssl.get("serial_number")
        return ScanChanges(
            scan_id=job_id,
            previous_scan_id=previous.id,
            score_delta=current_report.score - previous_report.score,
            added_findings=sorted(current_findings - previous_findings),
            resolved_findings=sorted(previous_findings - current_findings),
            added_ports=sorted(current_ports - previous_ports),
            removed_ports=sorted(previous_ports - current_ports),
            added_subdomains=sorted(current_subdomains - previous_subdomains),
            removed_subdomains=sorted(previous_subdomains - current_subdomains),
            certificate_changed=bool(
                current_serial and previous_serial and current_serial != previous_serial
            ),
        )
