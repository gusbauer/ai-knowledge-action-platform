from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def replace_for_document(
        self,
        document_id: int,
        chunks: list[str],
    ) -> list[DocumentChunk]:
        await self.session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )

        records = [
            DocumentChunk(
                document_id=document_id,
                position=position,
                content=content,
                character_count=len(content),
            )
            for position, content in enumerate(chunks)
        ]

        self.session.add_all(records)

        await self.session.commit()

        return records

    async def list_for_document(
        self,
        document_id: int,
    ) -> list[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.position)
        )

        return list(result.scalars().all())