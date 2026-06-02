import json
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings


@dataclass(slots=True)
class AIProviderClient:
    model_name: str = settings.openai_model
    client: Any | None = None

    async def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        response = await self._get_client().responses.create(
            model=self.model_name,
            input=prompt,
        )
        return self._extract_text(response)

    async def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        if not schema_name.strip():
            raise ValueError("schema_name must not be empty")

        json_prompt = (
            f"{prompt.strip()}\n\n"
            f"Return only valid JSON that matches the {schema_name} schema. "
            "Do not include Markdown, comments, or extra explanation."
        )
        text = await self.generate_text(json_prompt)
        parsed = json.loads(self._strip_json_fence(text))

        if not isinstance(parsed, dict):
            raise ValueError("AI JSON response must be an object")

        return parsed

    def _get_client(self) -> Any:
        if self.client is not None:
            return self.client

        if settings.openai_api_key_is_placeholder:
            raise RuntimeError("Set a real OPENAI_API_KEY in .env before calling the AI provider.")

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self.client

    @staticmethod
    def _extract_text(response: Any) -> str:
        output_text = getattr(response, "output_text", None)

        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        if isinstance(response, dict):
            output_text = response.get("output_text")
            if isinstance(output_text, str) and output_text.strip():
                return output_text.strip()

        raise ValueError("AI response did not contain output text")

    @staticmethod
    def _strip_json_fence(text: str) -> str:
        cleaned = text.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        return cleaned