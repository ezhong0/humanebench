"""OpenAI adapter for testing GPT models."""

from typing import List, Dict, Tuple
from .base_adapter import BaseAIAdapter


class OpenAIAdapter(BaseAIAdapter):
    """Adapter for OpenAI models (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, model: str, api_key: str, **kwargs):
        """Initialize OpenAI adapter."""
        super().__init__(model, api_key, **kwargs)

        try:
            import openai
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

        self.client = openai.OpenAI(api_key=api_key)

    def get_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str | None = None
    ) -> Tuple[str, Dict]:
        """Get response from OpenAI API."""

        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 1024),
        }

        # Add optional parameters
        if "top_p" in self.config:
            params["top_p"] = self.config["top_p"]

        # Make API call
        response = self.client.chat.completions.create(**params)

        # Extract response and metadata
        response_text = response.choices[0].message.content
        metadata = {
            "tokens_used": response.usage.total_tokens if response.usage else 0,
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
        }

        return response_text, metadata
