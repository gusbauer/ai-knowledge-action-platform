from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    filename: str = Field(
        min_length=1,
        max_length=255,
    )


class DocumentRead(BaseModel):
    id: int
    filename: str
    storage_path: str | None
    content_type: str | None
    size_bytes: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class DocumentContent(BaseModel):
    id: int
    filename: str
    content: str
    character_count: int
    
class DocumentChunkRead(BaseModel):
    id: int
    document_id: int
    position: int
    content: str
    character_count: int

    model_config = ConfigDict(from_attributes=True)


class DocumentChunkProcessResult(BaseModel):
    document_id: int
    chunk_count: int
    chunks: list[DocumentChunkRead]
    
class DocumentEmbeddingProcessResult(BaseModel):
    document_id: int
    chunk_count: int
    embedding_dimension: int
    model: str

class SemanticSearchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=500,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class SemanticSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    position: int
    content: str
    similarity: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]