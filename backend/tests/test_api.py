import httpx
import pytest
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as session:
        yield session


@pytest.mark.asyncio
async def test_health_exposes_current_version(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0-alpha.1"}
    assert response.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
async def test_scan_requires_authorization_confirmation(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/scans", json={"domain": "example.com", "authorized": False}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_deep_scan_requires_additional_confirmation(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/scans",
        json={"target": "example.com", "profile": "deep", "authorized": True},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_individual_delete_requires_confirmation(
    client: httpx.AsyncClient,
) -> None:
    response = await client.delete("/api/v1/scans/unknown")
    assert response.status_code == 400
    assert response.json()["detail"] == "La eliminación requiere confirm=true."
