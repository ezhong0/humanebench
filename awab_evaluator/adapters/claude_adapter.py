"""Claude/Anthropic adapter for testing Claude models."""

from typing import List, Dict, Tuple
from .base_adapter import BaseAIAdapter


class ClaudeAdapter(BaseAIAdapter):
    """Adapter for Anthropic Claude models."""

    def __init__(self, model: str, api_key: str, **kwargs):
        """Initialize Claude adapter."""
        super().__init__(model, api_key, **kwargs)

        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.client = anthropic.Anthropic(api_key=api_key)

    def get_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str | None = None
    ) -> Tuple[str, Dict]:
        """Get response from Claude API."""

        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.config.get("max_tokens", 1024),
            "temperature": self.config.get("temperature", 0.7),
        }

        # Add system prompt if provided
        if system_prompt:
            params["system"] = system_prompt

        # Add optional parameters
        if "top_p" in self.config:
            params["top_p"] = self.config["top_p"]

        # Make API call
        response = self.client.messages.create(**params)

        # Extract response and metadata
        response_text = response.content[0].text
        metadata = {
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "model": response.model,
            "stop_reason": response.stop_reason,
        }

        return response_text, metadata
