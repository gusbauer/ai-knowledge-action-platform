import pytest
from httpx import (
    ASGITransport,
    AsyncClient,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import get_db
from app.main import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_readiness_with_database(
    db_session: AsyncSession,
):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[
        get_db
    ] = override_get_db

    transport = ASGITransport(
        app=app
    )

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/health/ready"
            )

        assert (
            response.status_code == 200
        )

        body = response.json()

        assert (
            body["status"]
            == "ready"
        )

        assert (
            body["database"]
            == "connected"
        )

    finally:
        app.dependency_overrides.clear()