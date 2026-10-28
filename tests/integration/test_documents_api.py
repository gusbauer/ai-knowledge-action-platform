import pytest
from httpx import (
    ASGITransport,
    AsyncClient,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.main import app
from app.models.document import Document


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_documents_uses_test_database(
    db_session: AsyncSession,
):
    document = Document(
        filename="test-document.txt",
        storage_path=None,
        content_type="text/plain",
        size_bytes=50,
    )

    db_session.add(document)

    await db_session.commit()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[
        get_db
    ] = override_get_db

    try:
        transport = ASGITransport(
            app=app
        )

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/documents"
            )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1

    assert (
        body[0]["filename"]
        == "test-document.txt"
    )