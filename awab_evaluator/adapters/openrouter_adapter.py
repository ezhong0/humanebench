"""OpenRouter adapter for testing multiple models through OpenRouter API."""

from typing import List, Dict, Tuple
from .base_adapter import BaseAIAdapter


class OpenRouterAdapter(BaseAIAdapter):
    """Adapter for OpenRouter (provides access to many models)."""

    def __init__(self, model: str, api_key: str, **kwargs):
        """Initialize OpenRouter adapter."""
        super().__init__(model, api_key, **kwargs)

        try:
            import openai  # OpenRouter uses OpenAI-compatible API
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

        # OpenRouter uses OpenAI-compatible endpoint
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def get_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str | None = None
    ) -> Tuple[str, Dict]:
        """Get response from OpenRouter API."""

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

        # OpenRouter-specific headers (optional but recommended)
        extra_headers = {
            "HTTP-Referer": self.config.get("site_url", "https://github.com/humanebench"),
            "X-Title": self.config.get("site_name", "AWAB Benchmark"),
        }

        # Make API call
        response = self.client.chat.completions.create(
            **params,
            extra_headers=extra_headers
        )

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


# Popular OpenRouter model identifiers for reference
POPULAR_MODELS = {
    # OpenAI
    "gpt-4": "openai/gpt-4",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",

    # Anthropic
    "claude-3-opus": "anthropic/claude-3-opus",
    "claude-3-sonnet": "anthropic/claude-3-sonnet",
    "claude-3-haiku": "anthropic/claude-3-haiku",

    # Google
    "gemini-pro": "google/gemini-pro",
    "gemini-pro-vision": "google/gemini-pro-vision",

    # Meta
    "llama-3-70b": "meta-llama/llama-3-70b-instruct",
    "llama-3-8b": "meta-llama/llama-3-8b-instruct",

    # Mistral
    "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",

    # Others
    "perplexity": "perplexity/pplx-70b-online",
}
