import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError

class LLMProviderError(
    ExternalServiceError
):
    code = "llm_provider_unavailable"


class OllamaProvider:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise LLMProviderError(
                "Could not communicate with the LLM provider."
            ) from exc

        data = response.json()

        try:
            return data["message"]["content"].strip()

        except (KeyError, TypeError) as exc:
            raise LLMProviderError(
                "The LLM provider returned an invalid response."
            ) from exc