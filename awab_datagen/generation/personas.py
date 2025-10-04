"""Persona generation for test scenarios."""

import random
from typing import List
from ..core.models import Persona, ScenarioTemplate


class PersonaGenerator:
    """Generates diverse user personas for scenarios."""

    DISTRIBUTIONS = {
        "age_group": ["teen", "young_adult", "adult", "senior"],
        "context": ["isolated", "supported", "mixed"],
        "baseline_state": ["stable", "declining", "crisis"],
        "communication_style": ["direct", "indirect", "manipulative", "confused"],
        "cultural_context": ["western", "collectivist", "religious", "mixed"],
    }

    def __init__(self, seed: int | None = None):
        """
        Initialize persona generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

    def generate(
        self,
        scenario: ScenarioTemplate,
        n: int = 3,
        ensure_diversity: bool = True
    ) -> List[Persona]:
        """
        Generate n diverse personas for a scenario.

        Args:
            scenario: Scenario template to generate personas for
            n: Number of personas to generate
            ensure_diversity: If True, ensures personas are diverse

        Returns:
            List of generated personas
        """
        personas = []

        # Apply scenario-specific constraints if available
        constraints = scenario.persona_hints if hasattr(scenario, 'persona_hints') else {}

        # Generate personas
        for i in range(n):
            persona = Persona(
                age_group=self._sample("age_group", constraints, i if ensure_diversity else None),
                context=self._sample("context", constraints, i if ensure_diversity else None),
                baseline_state=self._sample("baseline_state", constraints, i if ensure_diversity else None),
                communication_style=self._sample("communication_style", constraints, i if ensure_diversity else None),
                cultural_context=self._sample("cultural_context", constraints, i if ensure_diversity else None),
            )
            personas.append(persona)

        return personas

    def _sample(
        self,
        field: str,
        constraints: dict,
        diversity_index: int | None = None
    ) -> str:
        """
        Sample a value for a persona field.

        Args:
            field: Persona field to sample
            constraints: Constraints from scenario template
            diversity_index: Index to ensure diversity (if provided)

        Returns:
            Sampled value
        """
        options = constraints.get(field, self.DISTRIBUTIONS[field])

        if diversity_index is not None and len(options) > 1:
            # Cycle through options to ensure diversity
            return options[diversity_index % len(options)]
        else:
            return random.choice(options)

    def generate_specific(
        self,
        age_group: str | None = None,
        context: str | None = None,
        baseline_state: str | None = None,
        communication_style: str | None = None,
        cultural_context: str | None = None,
    ) -> Persona:
        """
        Generate a persona with specific attributes.

        Args:
            age_group: Specific age group or None for random
            context: Specific context or None for random
            baseline_state: Specific baseline state or None for random
            communication_style: Specific communication style or None for random
            cultural_context: Specific cultural context or None for random

        Returns:
            Generated persona
        """
        return Persona(
            age_group=age_group or random.choice(self.DISTRIBUTIONS["age_group"]),
            context=context or random.choice(self.DISTRIBUTIONS["context"]),
            baseline_state=baseline_state or random.choice(self.DISTRIBUTIONS["baseline_state"]),
            communication_style=communication_style or random.choice(self.DISTRIBUTIONS["communication_style"]),
            cultural_context=cultural_context or random.choice(self.DISTRIBUTIONS["cultural_context"]),
        )
