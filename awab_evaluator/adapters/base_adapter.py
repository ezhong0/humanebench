"""Base adapter class for AI systems."""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import time


class BaseAIAdapter(ABC):
    """Abstract base class for AI system adapters."""

    def __init__(self, model: str, api_key: str, **kwargs):
        """
        Initialize adapter.

        Args:
            model: Model identifier
            api_key: API key for the service
            **kwargs: Additional configuration
        """
        self.model = model
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def get_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str | None = None
    ) -> Tuple[str, Dict]:
        """
        Get response from AI system.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt

        Returns:
            Tuple of (response_text, metadata)
            metadata includes: response_time_ms, tokens_used, etc.
        """
        pass

    def format_conversation(self, user_messages: List[str]) -> List[Dict[str, str]]:
        """
        Format user messages into conversation format.

        Args:
            user_messages: List of user messages

        Returns:
            List of message dicts with role and content
        """
        messages = []
        for msg in user_messages:
            messages.append({"role": "user", "content": msg})
            # For multi-turn, we might want to add assistant responses
            # but for testing, we just send all user messages
        return messages

    def test_response(
        self,
        user_messages: List[str],
        system_prompt: str | None = None
    ) -> Tuple[str, float, int]:
        """
        Get response with timing.

        Args:
            user_messages: List of user messages
            system_prompt: Optional system prompt

        Returns:
            Tuple of (response, response_time_ms, tokens_used)
        """
        messages = self.format_conversation(user_messages)

        start_time = time.time()
        response, metadata = self.get_response(messages, system_prompt)
        response_time_ms = (time.time() - start_time) * 1000

        tokens_used = metadata.get("tokens_used", 0)

        return response, response_time_ms, tokens_used
