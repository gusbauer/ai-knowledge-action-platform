from unittest.mock import patch

from app.agents.model_factory import (
    build_agent_model,
)


def test_builds_ollama_model():
    with patch(
        "app.agents.model_factory.settings.llm_provider",
        "ollama",
    ):
        model = build_agent_model()

        assert model is not None