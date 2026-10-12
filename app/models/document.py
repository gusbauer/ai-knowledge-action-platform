from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )