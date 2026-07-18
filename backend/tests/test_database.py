from datetime import timedelta

import pytest
import pytest_asyncio
from sqlalchemy import update

from app.database import ScanRecord, ScanRepository, utcnow
from app.models import (
    CategoryScore,
    ConfidenceLevel,
    Coverage,
    RiskLevel,
    ScanProfile,
    ScanReport,
    ScanStatus,
)


def report(domain: str = "example.com", score: int = 90, port: int = 443) -> ScanReport:
    return ScanReport(
        input_target=domain,
        domain=domain,
        profile=ScanProfile.STANDARD,
        generated_at=utcnow(),
        duration_seconds=1.2,
        score=score,
        grade="A" if score >= 90 else "B",
        risk_level=RiskLevel.LOW if score >= 85 else RiskLevel.MODERATE,
        confidence=ConfidenceLevel.HIGH,
        coverage_percent=100,
        coverage=Coverage(
            completed_modules=["dns"],
            expected_modules=["dns"],
            missing_modules=[],
            percent=100,
        ),
        category_scores={"dns_email": CategoryScore(score=score, weight=20)},
        ruleset_version="2.0.0",
        summary="Resumen",
        top_actions=[],
        findings=[],
        ip_addresses=["93.184.216.34"],
        whois={},
        domain_identity={},
        dns={},
        email_security={},
        ssl={"serial_number": "one"},
        web_security={},
        subdomains=[],
        http={},
        ports=[{"port": port, "protocol": "tcp", "service": "https", "risk": False}],
        reputation={},
        errors={},
    )


@pytest_asyncio.fixture
async def repository(tmp_path):
    repo = ScanRepository(f"sqlite+aiosqlite:///{tmp_path / 'history.db'}")
    await repo.initialize()
    yield repo
    await repo.close()


@pytest.mark.asyncio
async def test_history_persists_completed_report(repository: ScanRepository) -> None:
    job = await repository.create_job(
        job_id="one",
        input_target="https://example.com/path",
        domain="example.com",
        profile=ScanProfile.STANDARD,
        options={},
    )
    assert job.status == ScanStatus.QUEUED
    await repository.complete(job.id, report())
    stored = await repository.get(job.id)
    assert stored and stored.report and stored.report.score == 90
    page = await repository.list(query="example")
    assert page.total == 1
    assert page.items[0].input_target == "https://example.com/path"


@pytest.mark.asyncio
async def test_restart_marks_running_jobs_as_interrupted(
    repository: ScanRepository,
) -> None:
    await repository.create_job(
        job_id="running",
        input_target="example.com",
        domain="example.com",
        profile=ScanProfile.QUICK,
        options={},
    )
    await repository.update_progress("running", ScanStatus.RUNNING, "DNS", 20)
    assert await repository.mark_interrupted() == 1
    stored = await repository.get("running")
    assert stored and stored.status == ScanStatus.INTERRUPTED
    assert "reiniciarse" in (stored.error or "")


@pytest.mark.asyncio
async def test_retention_cleanup_and_delete(repository: ScanRepository) -> None:
    await repository.create_job(
        job_id="old",
        input_target="old.example.com",
        domain="old.example.com",
        profile=ScanProfile.QUICK,
        options={},
    )
    async with repository.sessions() as session:
        await session.execute(
            update(ScanRecord)
            .where(ScanRecord.id == "old")
            .values(created_at=utcnow() - timedelta(days=91))
        )
        await session.commit()
    assert await repository.cleanup(90) == 1
    assert await repository.get("old") is None


@pytest.mark.asyncio
async def test_comparison_detects_score_and_port_changes(
    repository: ScanRepository,
) -> None:
    first = await repository.create_job(
        job_id="first",
        input_target="example.com",
        domain="example.com",
        profile=ScanProfile.STANDARD,
        options={},
    )
    await repository.complete(first.id, report(score=80, port=80))
    second = await repository.create_job(
        job_id="second",
        input_target="example.com",
        domain="example.com",
        profile=ScanProfile.STANDARD,
        options={},
    )
    await repository.complete(second.id, report(score=90, port=443))
    changes = await repository.changes(second.id)
    assert changes and changes.score_delta == 10
    assert changes.added_ports == [443]
    assert changes.removed_ports == [80]


@pytest.mark.asyncio
async def test_history_filters_dates_and_paginates(
    repository: ScanRepository,
) -> None:
    for index in range(4):
        await repository.create_job(
            job_id=f"page-{index}",
            input_target=f"host-{index}.example.com",
            domain=f"host-{index}.example.com",
            profile=ScanProfile.QUICK if index < 3 else ScanProfile.STANDARD,
            options={},
        )
    now = utcnow()
    async with repository.sessions() as session:
        await session.execute(
            update(ScanRecord)
            .where(ScanRecord.id == "page-0")
            .values(created_at=now - timedelta(days=10))
        )
        await session.commit()

    first_page = await repository.list(
        profile=ScanProfile.QUICK,
        date_from=now - timedelta(days=5),
        limit=1,
        offset=0,
    )
    second_page = await repository.list(
        profile=ScanProfile.QUICK,
        date_from=now - timedelta(days=5),
        limit=1,
        offset=1,
    )
    assert first_page.total == 2
    assert len(first_page.items) == 1
    assert len(second_page.items) == 1
    assert first_page.items[0].id != second_page.items[0].id
