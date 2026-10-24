from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from pgvector.psycopg import register_vector_async
from sqlalchemy import event
from app.core.config import settings


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
@event.listens_for(engine.sync_engine, "connect")
def register_vector(
    dbapi_connection,
    connection_record,
):
    dbapi_connection.run_async(
        register_vector_async
    )