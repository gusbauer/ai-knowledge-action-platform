from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class AgentRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    min_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )

    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )

    @field_validator(
        "question"
    )
    @classmethod
    def validate_question(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if len(normalized) < 3:
            raise ValueError(
                "Question must contain "
                "at least 3 characters."
            )

        return normalized


class AgentSource(BaseModel):
    chunk_id: int
    document_id: int
    position: int
    similarity: float
    content: str


class AgentResponse(BaseModel):
    thread_id: str

    status: Literal[
        "completed",
        "interrupted",
    ]

    question: str | None = None

    answer: str | None = None

    route: Literal[
        "knowledge",
        "system",
    ] | None = None

    handled_by: Literal[
        "knowledge",
        "system",
    ] | None = None

    tool_used: str | None = None

    sources: list[
        AgentSource
    ] = Field(
        default_factory=list
    )

    interrupt: dict[
        str,
        Any,
    ] | None = None


class AgentResumeRequest(BaseModel):
    thread_id: str = Field(
        min_length=1,
        max_length=128,
    )

    approved: bool

    note: str | None = Field(
        default=None,
        max_length=500,
    )