"""Factory for creating AI provider instances"""

from .base import AIProviderBase
from .openai_provider import OpenAIProvider
from app.core.config import settings


def get_ai_provider(provider_name: str) -> AIProviderBase:
    """
    Get an AI provider instance based on the provider name

    Args:
        provider_name: Name of the provider ("openai", "anthropic", "gemini")

    Returns:
        An instance of AIProviderBase

    Raises:
        ValueError: If the provider is not supported or API key is missing
    """
    provider_name = provider_name.lower()

    if provider_name == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "AI機能は現在利用できません。OpenAI APIキーが設定されていません。"
            )
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.AI_REQUEST_TIMEOUT,
            max_retries=settings.AI_MAX_RETRIES,
        )

    elif provider_name == "anthropic":
        # Import here to avoid circular dependency
        from .anthropic_provider import AnthropicProvider

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError(
                "AI機能は現在利用できません。Anthropic APIキーが設定されていません。"
            )
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=settings.AI_REQUEST_TIMEOUT,
            max_retries=settings.AI_MAX_RETRIES,
        )

    elif provider_name == "gemini":
        # Import here to avoid circular dependency
        from .gemini_provider import GeminiProvider

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "AI機能は現在利用できません。Gemini APIキーが設定されていません。"
            )
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY, timeout=settings.AI_REQUEST_TIMEOUT
        )

    else:
        raise ValueError(
            f"Unsupported AI provider: {provider_name}. Supported providers: openai, anthropic, gemini"
        )
