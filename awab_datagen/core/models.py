"""Core data models for AWAB benchmark."""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from enum import Enum


class Domain(str, Enum):
    """Test domains for AWAB benchmark."""
    MENTAL_HEALTH = "mental_health"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    RELATIONSHIPS = "relationships"
    ADDICTION = "addiction"
    SELF_IMAGE = "self_image"
    MISINFORMATION = "misinformation"
    LIFE_DECISIONS = "life_decisions"


class HarmPattern(str, Enum):
    """Patterns of harmful requests."""
    DIRECT = "direct"
    HIDDEN = "hidden"
    RATIONALIZED = "rationalized"
    MISINFORMED = "misinformed"


class VulnerabilityLevel(str, Enum):
    """User vulnerability levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Persona(BaseModel):
    """User persona with 5 key variables."""
    age_group: Literal["teen", "young_adult", "adult", "senior"]
    context: Literal["isolated", "supported", "mixed"]
    baseline_state: Literal["stable", "declining", "crisis"]
    communication_style: Literal["direct", "indirect", "manipulative", "confused"]
    cultural_context: Literal["western", "collectivist", "religious", "mixed"]

    def to_description(self) -> str:
        """Convert persona to readable description."""
        return (
            f"{self.age_group} {self.context}, "
            f"{self.baseline_state}, "
            f"{self.communication_style}, "
            f"{self.cultural_context}"
        )


class ConversationTurn(BaseModel):
    """Single turn in a conversation."""
    role: Literal["user", "assistant"]
    content: str


class ScenarioTemplate(BaseModel):
    """Template for generating test scenarios."""
    id: str
    domain: Domain
    harm_pattern: HarmPattern
    vulnerability_level: VulnerabilityLevel
    description: str
    user_message_templates: list[str | dict[str, str]]
    conversation_type: Literal["single_turn", "multi_turn"]
    multi_turn_pattern: Optional[Literal["escalation", "manipulation", "hidden_signal"]] = None
    persona_hints: dict[str, list[str]] = Field(default_factory=dict)
    required_ground_truth: Optional[dict[str, Any]] = None


class GroundTruth(BaseModel):
    """Ground truth annotations for evaluation."""
    safety: Literal["safe", "unsafe"]
    principle_scores: dict[str, int] = Field(
        description="Scores 1-5 for safety_dignity, longterm_wellbeing, transparency"
    )
    required_actions: list[str]
    meets_requirements: bool
    annotator_notes: Optional[str] = None


class DataPoint(BaseModel):
    """Single data point in the dataset."""
    id: str
    domain: Domain
    harm_pattern: HarmPattern
    vulnerability_level: VulnerabilityLevel
    persona: Persona
    conversation: list[ConversationTurn]
    ground_truth: Optional[GroundTruth] = None
    metadata: dict = Field(default_factory=dict)
