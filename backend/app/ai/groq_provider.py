"""
Groq AI Provider (FREE tier).
Uses OpenAI-compatible API with Llama 3.3 70B for structured JSON output.
"""

import json
import time
import logging
from typing import Optional

from app.ai.provider import AIProvider, AIResponse
from app.config import settings

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    """Groq Llama 3.3 70B - fallback free AI provider (ultra-fast inference)."""

    def __init__(self):
        self._client = None
        if self.is_available():
            try:
                from groq import Groq
                self._client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info(f"Groq provider initialized with model: {settings.GROQ_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq provider: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> AIResponse:
        """Generate structured JSON output using Groq."""
        if not self._client:
            return AIResponse(success=False, error="Groq provider not initialized")

        start = time.time()
        try:
            system_msg = system_prompt or "You are a precise AI assistant."
            system_msg += f"\n\nIMPORTANT: Respond ONLY with valid JSON matching this exact schema. No markdown, no code blocks, no extra text.\nRequired JSON Schema:\n{json.dumps(schema, indent=2)}"

            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ]

            effective_tokens = min(max_tokens, 4096)
            response = self._client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=effective_tokens,
                response_format={"type": "json_object"},
            )

            latency = (time.time() - start) * 1000
            content = response.choices[0].message.content.strip()

            # Parse JSON
            try:
                structured_data = json.loads(content)
            except json.JSONDecodeError:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                structured_data = json.loads(content)

            return AIResponse(
                content=content,
                structured_data=structured_data,
                model=settings.GROQ_MODEL,
                provider="groq",
                tokens_used=response.usage.total_tokens if response.usage else 0,
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Groq generation failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                provider="groq",
                model=settings.GROQ_MODEL,
                latency_ms=latency,
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """Generate free-form text output."""
        if not self._client:
            return AIResponse(success=False, error="Groq provider not initialized")

        start = time.time()
        try:
            messages = [
                {"role": "system", "content": system_prompt or "You are a precise AI assistant."},
                {"role": "user", "content": prompt},
            ]

            effective_tokens = min(max_tokens, 980)
            response = self._client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=effective_tokens,
            )

            latency = (time.time() - start) * 1000
            return AIResponse(
                content=response.choices[0].message.content.strip(),
                model=settings.GROQ_MODEL,
                provider="groq",
                tokens_used=response.usage.total_tokens if response.usage else 0,
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Groq text generation failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                provider="groq",
                model=settings.GROQ_MODEL,
                latency_ms=latency,
            )

    def get_provider_name(self) -> str:
        return "groq"

    def get_model_name(self) -> str:
        return settings.GROQ_MODEL

    def is_available(self) -> bool:
        return bool(settings.GROQ_API_KEY)
