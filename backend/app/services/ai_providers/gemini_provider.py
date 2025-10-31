"""Google Gemini provider implementation"""

import asyncio
import google.generativeai as genai
from .base import AIProviderBase


class GeminiProvider(AIProviderBase):
    """Google Gemini API provider implementation"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Gemini provider

        Args:
            api_key: Google Gemini API key
            timeout: Request timeout in seconds
        """
        genai.configure(api_key=api_key)

        # Initialize model with system instruction
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="あなたは創造的なアイデアを生成するアシスタントです。ユーザーのノートを基に、新しい洞察やアイデアを提供してください。",
        )
        self.timeout = timeout

    async def generate(self, prompt: str, context: str) -> str:
        """
        Generate content using Google Gemini API

        Args:
            prompt: The user's prompt/instruction
            context: The context from selected notes

        Returns:
            Generated content as string

        Raises:
            Exception: If the Gemini API call fails
        """
        try:
            # Construct the user prompt with context
            full_prompt = f"{prompt}\n\nコンテキスト:\n{context}"

            # Generate content with timeout
            response = await asyncio.wait_for(
                self.model.generate_content_async(full_prompt), timeout=self.timeout
            )

            # Return the generated text
            return response.text if response.text else ""

        except asyncio.TimeoutError:
            raise Exception(
                f"Gemini API request timed out after {self.timeout} seconds"
            )
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Gemini API error: {str(e)}") from e

    def get_max_tokens(self) -> int:
        """
        Get the maximum token limit for Google Gemini

        Returns:
            Maximum number of tokens (1000000 for Gemini 2.5 Flash)
        """
        return 1000000
