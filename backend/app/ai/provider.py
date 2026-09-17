"""
AI Provider Abstract Interface (§49, §51).
Defines the contract for all AI providers - enables provider/model independence.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


class AIResponse(BaseModel):
    """Standardized response from any AI provider."""

    content: str = ""
    structured_data: Optional[dict] = None
    model: str = ""
    provider: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class AIProvider(ABC):
    """Abstract interface for AI providers. All providers must implement this."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> AIResponse:
        """Generate structured JSON output conforming to a schema."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """Generate free-form text output."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'gemini', 'groq')."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name being used."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass
