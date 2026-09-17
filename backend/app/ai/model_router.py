"""
Model Router (§51) - Routes AI requests to appropriate provider with automatic fallback.
"""

import logging
from typing import Optional

from app.ai.provider import AIProvider, AIResponse
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.config import settings

logger = logging.getLogger(__name__)


class ModelRouter:
    """
    Routes AI requests to the appropriate provider.
    Supports automatic fallback on failure (§51).
    """

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}
        self._cooldowns: dict[str, float] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        gemini = GeminiProvider()
        if gemini.is_available():
            self._providers["gemini"] = gemini
            logger.info("Gemini provider registered")

        groq = GroqProvider()
        if groq.is_available():
            self._providers["groq"] = groq
            logger.info("Groq provider registered")

        if not self._providers:
            logger.warning("No AI providers available! Configure GEMINI_API_KEY or GROQ_API_KEY")

    def get_primary_provider(self) -> Optional[AIProvider]:
        """Get the primary configured provider."""
        return self._providers.get(settings.PRIMARY_AI_PROVIDER)

    def get_fallback_provider(self) -> Optional[AIProvider]:
        """Get the fallback provider."""
        return self._providers.get(settings.FALLBACK_AI_PROVIDER)

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.1,
        max_tokens: int = 8192,
        preferred_provider: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate structured output with automatic fallback.
        Tries primary provider first, falls back to secondary on failure.
        """
        import time
        providers_to_try = self._get_provider_order(preferred_provider)

        for provider_name, provider in providers_to_try:
            logger.info(f"Attempting structured generation with {provider_name}")
            response = await provider.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if response.success:
                logger.info(f"Structured generation successful with {provider_name} ({response.latency_ms:.0f}ms)")
                return response
            else:
                err_str = str(response.error or "")
                if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower():
                    # Set cooldown for this provider for 180 seconds to avoid repeated 429 stalls
                    self._cooldowns[provider_name] = time.time() + 180.0
                    logger.warning(f"{provider_name} rate-limited / quota exceeded. Cooldown active for 3 minutes.")
                else:
                    logger.warning(f"{provider_name} failed: {response.error}. Trying fallback...")

        return AIResponse(
            success=False,
            error="All AI providers failed. Please check your API keys.",
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        preferred_provider: Optional[str] = None,
    ) -> AIResponse:
        """Generate text with automatic fallback."""
        providers_to_try = self._get_provider_order(preferred_provider)

        for provider_name, provider in providers_to_try:
            logger.info(f"Attempting text generation with {provider_name}")
            response = await provider.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if response.success:
                return response
            else:
                logger.warning(f"{provider_name} failed: {response.error}. Trying fallback...")

        return AIResponse(
            success=False,
            error="All AI providers failed. Please check your API keys.",
        )

    def _get_provider_order(self, preferred: Optional[str] = None) -> list[tuple[str, AIProvider]]:
        """Determine provider order based on preference and availability, prioritizing non-cooldown providers."""
        import time
        now = time.time()
        raw_order = []

        if preferred and preferred in self._providers:
            raw_order.append((preferred, self._providers[preferred]))

        primary = settings.PRIMARY_AI_PROVIDER
        if primary in self._providers and primary != preferred:
            raw_order.append((primary, self._providers[primary]))

        fallback = settings.FALLBACK_AI_PROVIDER
        if fallback in self._providers and fallback != preferred and fallback != primary:
            raw_order.append((fallback, self._providers[fallback]))

        # Add any remaining providers
        for name, provider in self._providers.items():
            if not any(name == n for n, _ in raw_order):
                raw_order.append((name, provider))

        active_order = []
        cooling_order = []
        for name, prov in raw_order:
            if self._cooldowns.get(name, 0) > now:
                cooling_order.append((name, prov))
            else:
                active_order.append((name, prov))

        return active_order + cooling_order

    def get_available_providers(self) -> list[str]:
        """List available provider names."""
        return list(self._providers.keys())


# Singleton instance
_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get or create the model router singleton."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
