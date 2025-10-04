"""Conversation generation for test scenarios."""

import random
from typing import List
from jinja2 import Template
from ..core.models import ScenarioTemplate, Persona, ConversationTurn
from .llm import LLMClient


class ConversationGenerator:
    """Generates conversations based on scenarios and personas."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize conversation generator.

        Args:
            llm_client: LLM client for generating AI responses
        """
        self.llm = llm_client

    def generate(
        self,
        scenario: ScenarioTemplate,
        persona: Persona,
        generate_ai_responses: bool = False,
        template_index: int = None
    ) -> List[ConversationTurn]:
        """
        Generate conversation based on scenario and persona.

        Args:
            scenario: Scenario template
            persona: User persona
            generate_ai_responses: If True, generate AI responses using LLM
            template_index: Index to select from template variants (cycles through)

        Returns:
            List of conversation turns
        """
        if scenario.conversation_type == "single_turn":
            return self._generate_single_turn(scenario, persona, generate_ai_responses, template_index)
        else:
            return self._generate_multi_turn(scenario, persona, generate_ai_responses, template_index)

    def _generate_single_turn(
        self,
        scenario: ScenarioTemplate,
        persona: Persona,
        generate_ai_response: bool,
        template_index: int = None
    ) -> List[ConversationTurn]:
        """Generate single-turn conversation."""
        # Select template (cycle through if index provided, otherwise random)
        if template_index is not None:
            idx = template_index % len(scenario.user_message_templates)
            template_str = scenario.user_message_templates[idx]
        else:
            template_str = random.choice(scenario.user_message_templates)

        # Handle string templates
        if isinstance(template_str, str):
            user_message = self._render_template(template_str, persona, scenario)
            turns = [ConversationTurn(role="user", content=user_message)]

            if generate_ai_response:
                ai_response = self._generate_ai_response([turns[0]])
                turns.append(ConversationTurn(role="assistant", content=ai_response))

            return turns

        # Handle dict templates (shouldn't happen for single-turn)
        raise ValueError("Single-turn scenarios should have string templates")

    def _generate_multi_turn(
        self,
        scenario: ScenarioTemplate,
        persona: Persona,
        generate_ai_responses: bool,
        template_index: int = None
    ) -> List[ConversationTurn]:
        """Generate multi-turn conversation with pattern."""
        turns = []
        # Select template (cycle through if index provided, otherwise random)
        if template_index is not None:
            idx = template_index % len(scenario.user_message_templates)
            template = scenario.user_message_templates[idx]
        else:
            template = random.choice(scenario.user_message_templates)

        # Handle dict templates for multi-turn
        if isinstance(template, dict):
            for turn_key in sorted(template.keys()):
                # Render user message
                user_msg = self._render_template(
                    template[turn_key], persona, scenario
                )
                turns.append(ConversationTurn(role="user", content=user_msg))

                # Generate AI response if requested
                if generate_ai_responses:
                    ai_response = self._generate_ai_response(turns)
                    turns.append(ConversationTurn(role="assistant", content=ai_response))

            return turns

        # Fallback for string templates in multi-turn (treat as single message)
        user_message = self._render_template(template, persona, scenario)
        turns = [ConversationTurn(role="user", content=user_message)]

        if generate_ai_responses:
            ai_response = self._generate_ai_response(turns)
            turns.append(ConversationTurn(role="assistant", content=ai_response))

        return turns

    def _render_template(
        self,
        template_str: str,
        persona: Persona,
        scenario: ScenarioTemplate
    ) -> str:
        """
        Return template string as-is (persona rendering disabled).

        Args:
            template_str: Template string
            persona: User persona (unused)
            scenario: Scenario template (unused)

        Returns:
            Raw template message
        """
        # Just return the template without rendering
        # This gives us variety through different templates, not personas
        return template_str

    def _age_from_group(self, age_group: str) -> int:
        """Convert age group to approximate age."""
        mapping = {
            "teen": 16,
            "young_adult": 24,
            "adult": 40,
            "senior": 68
        }
        return mapping.get(age_group, 30)

    def _generate_ai_response(self, conversation_so_far: List[ConversationTurn]) -> str:
        """
        Generate AI response using LLM.

        Args:
            conversation_so_far: Conversation history

        Returns:
            AI response
        """
        # Convert to messages format
        messages = [
            {"role": turn.role, "content": turn.content}
            for turn in conversation_so_far
        ]

        # Generate response
        return self.llm.generate(messages)
