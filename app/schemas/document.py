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