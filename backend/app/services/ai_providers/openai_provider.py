"""OpenAI provider implementation"""

import asyncio
from openai import AsyncOpenAI
from .base import AIProviderBase


class OpenAIProvider(AIProviderBase):
    """OpenAI API provider implementation"""

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.client = AsyncOpenAI(
            api_key=api_key, timeout=timeout, max_retries=max_retries
        )

    async def generate(self, prompt: str, context: str) -> str:
        """
        Generate content using OpenAI API

        Args:
            prompt: The user's prompt/instruction
            context: The context from selected notes

        Returns:
            Generated content as string

        Raises:
            Exception: If the OpenAI API call fails
        """
        try:
            # Construct the full input with system instruction and context
            system_instruction = "あなたは創造的なアイデアを生成するアシスタントです。ユーザーのノートを基に、新しい洞察やアイデアを提供してください。"
            full_input = f"{system_instruction}\n\n{prompt}\n\nコンテキスト:\n{context}"

            # Use the new Responses API with gpt-5-nano model
            response = await self.client.responses.create(
                model="gpt-5-nano", input=full_input, store=True
            )

            return response.output_text or ""

        except Exception as e:
            # Re-raise with more context
            raise Exception(f"OpenAI API error: {str(e)}") from e

    def get_max_tokens(self) -> int:
        """
        Get the maximum token limit for OpenAI GPT-5-nano

        Returns:
            Maximum number of tokens for GPT-5-nano
        """
        return 128000
