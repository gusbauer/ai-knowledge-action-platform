from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        filename: str,
        storage_path: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
    ) -> Document:
        document = Document(
            filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
        )

        self.session.add(document)

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def list_all(self) -> list[Document]:
        result = await self.session.execute(
            select(Document).order_by(Document.id)
        )

        return list(result.scalars().all())
    
    async def get_by_id(
        self,
        document_id: int,
    ) -> Document | None:
        result = await self.session.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        return result.scalar_one_or_none()