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
    async def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        result = await self.session.execute(
            select(
                DocumentChunk,
                distance.label("distance"),
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )

        return [
            (chunk, float(distance_value))
            for chunk, distance_value in result.all()
        ]

    async def save_embeddings(
        self,
        document_id: int,
        embeddings: list[list[float]],
    ) -> list[DocumentChunk]:
        chunks = await self.list_for_document(
            document_id
        )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of embeddings does not "
                "match the number of chunks."
            )

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        ):
            chunk.embedding = embedding

        await self.session.commit()

        return chunks
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