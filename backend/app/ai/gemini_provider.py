"""
Google Gemini AI Provider (FREE tier).
Uses google-generativeai SDK with structured JSON output support.
"""

import json
import time
import logging
from typing import Optional

from app.ai.provider import AIProvider, AIResponse
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini Flash - primary free AI provider."""

    def __init__(self):
        self._model = None
        self._client = None
        if self.is_available():
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._client = genai
                self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info(f"Gemini provider initialized with model: {settings.GEMINI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini provider: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> AIResponse:
        """Generate structured JSON output using Gemini's native JSON mode."""
        if not self._model:
            return AIResponse(success=False, error="Gemini provider not initialized")

        start = time.time()
        try:
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System Instructions:\n{system_prompt}\n\n"

            full_prompt += f"{prompt}\n\n"
            full_prompt += f"IMPORTANT: Respond ONLY with valid JSON matching this exact schema. No markdown, no code blocks, no extra text.\n"
            full_prompt += f"Required JSON Schema:\n{json.dumps(schema, indent=2)}"

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "response_mime_type": "application/json",
            }

            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )

            latency = (time.time() - start) * 1000
            content = response.text.strip()

            # Parse JSON
            try:
                structured_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                structured_data = json.loads(content)

            return AIResponse(
                content=content,
                structured_data=structured_data,
                model=settings.GEMINI_MODEL,
                provider="gemini",
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Gemini generation failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                provider="gemini",
                model=settings.GEMINI_MODEL,
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
        if not self._model:
            return AIResponse(success=False, error="Gemini provider not initialized")

        start = time.time()
        try:
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System Instructions:\n{system_prompt}\n\n"
            full_prompt += prompt

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )

            latency = (time.time() - start) * 1000
            return AIResponse(
                content=response.text.strip(),
                model=settings.GEMINI_MODEL,
                provider="gemini",
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Gemini text generation failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                provider="gemini",
                model=settings.GEMINI_MODEL,
                latency_ms=latency,
            )

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return settings.GEMINI_MODEL

    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)
