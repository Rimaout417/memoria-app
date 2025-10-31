"""Anthropic (Claude) provider implementation"""

import asyncio
from anthropic import AsyncAnthropic
from .base import AIProviderBase


class AnthropicProvider(AIProviderBase):
    """Anthropic Claude API provider implementation"""

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.client = AsyncAnthropic(
            api_key=api_key, timeout=timeout, max_retries=max_retries
        )

    async def generate(self, prompt: str, context: str) -> str:
        """
        Generate content using Anthropic Claude API

        Args:
            prompt: The user's prompt/instruction
            context: The context from selected notes

        Returns:
            Generated content as string

        Raises:
            Exception: If the Anthropic API call fails
        """
        try:
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\nコンテキスト:\n{context}"}
                ],
                system="あなたは創造的なアイデアを生成するアシスタントです。ユーザーのノートを基に、新しい洞察やアイデアを提供してください。",
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""

        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Anthropic API error: {str(e)}") from e

    def get_max_tokens(self) -> int:
        """
        Get the maximum token limit for Anthropic Claude

        Returns:
            Maximum number of tokens (100000 for Claude 3)
        """
        return 100000
