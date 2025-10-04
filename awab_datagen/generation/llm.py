"""LLM client abstraction for conversation generation."""

from abc import ABC, abstractmethod
from typing import List, Dict


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass


class ClaudeClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key
            model: Model to use
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text using Claude API.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            Generated text
        """
        # Set defaults
        params = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": messages,
        }

        # Add optional parameters
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        if "system" in kwargs:
            params["system"] = kwargs["system"]

        response = self.client.messages.create(**params)
        return response.content[0].text


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, api_key: str, model: str = "gpt-5-mini"):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text using OpenAI API.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            Generated text
        """
        # Set defaults
        params = {
            "model": self.model,
            "messages": messages,
        }

        # Add optional parameters
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content


class MockLLMClient(LLMClient):
    """Mock LLM client for testing (doesn't require API key)."""

    def __init__(self):
        """Initialize mock client."""
        pass

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate mock response.

        Args:
            messages: List of message dicts
            **kwargs: Ignored

        Returns:
            Mock response
        """
        return "[Mock AI Response - Replace with real LLM for production use]"
