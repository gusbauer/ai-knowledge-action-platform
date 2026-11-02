import pytest

from pydantic import (
    ValidationError,
)

from app.schemas.agent import (
    AgentRequest,
)


def test_agent_question_is_trimmed():
    request = AgentRequest(
        question="   ¿Qué es RAG?   "
    )

    assert (
        request.question
        == "¿Qué es RAG?"
    )


def test_agent_rejects_blank_question():
    with pytest.raises(
        ValidationError
    ):
        AgentRequest(
            question="      "
        )