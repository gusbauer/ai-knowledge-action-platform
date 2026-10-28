import asyncio
import os
import selectors
import sys
from collections.abc import AsyncGenerator

import pytest_asyncio
from pgvector.psycopg import register_vector_async
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    (
        "postgresql+psycopg://"
        "ai_platform_test:"
        "ai_platform_test@"
        "localhost:5433/"
        "ai_platform_test"
    ),
)


def selector_loop_factory():
    return asyncio.SelectorEventLoop(
        selectors.SelectSelector()
    )


def pytest_asyncio_loop_factories(
    config,
    item,
):
    if sys.platform == "win32":
        return {
            "selector": selector_loop_factory,
        }

    return {
        "default": asyncio.new_event_loop,
    }


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    bootstrap_engine = create_async_engine(
        TEST_DATABASE_URL
    )

    async with bootstrap_engine.begin() as connection:
        await connection.execute(
            text(
                "CREATE EXTENSION IF NOT EXISTS vector"
            )
        )

    await bootstrap_engine.dispose()

    engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
    )

    @event.listens_for(
        engine.sync_engine,
        "connect",
    )
    def register_vector(
        dbapi_connection,
        connection_record,
    ):
        dbapi_connection.run_async(
            register_vector_async
        )

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )

        await connection.run_sync(
            Base.metadata.create_all
        )

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

        await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )

    await engine.dispose()