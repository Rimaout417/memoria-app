"""Base class for AI providers"""

from abc import ABC, abstractmethod


class AIProviderBase(ABC):
    """Base class for all AI providers"""

    @abstractmethod
    async def generate(self, prompt: str, context: str) -> str:
        """
        Generate content using the AI provider

        Args:
            prompt: The user's prompt/instruction
            context: The context from selected notes

        Returns:
            Generated content as string

        Raises:
            Exception: If the AI API call fails
        """
        pass

    @abstractmethod
    def get_max_tokens(self) -> int:
        """
        Get the maximum token limit for this provider

        Returns:
            Maximum number of tokens
        """
        pass
