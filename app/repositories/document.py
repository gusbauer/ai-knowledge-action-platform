from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, filename: str) -> Document:
        document = Document(filename=filename)

        self.session.add(document)

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def list_all(self) -> list[Document]:
        result = await self.session.execute(
            select(Document).order_by(Document.id)
        )

        return list(result.scalars().all())