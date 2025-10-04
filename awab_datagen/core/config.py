"""Configuration for AWAB data generation pipeline."""

from pydantic import BaseModel, Field
from pathlib import Path


class PipelineConfig(BaseModel):
    """Configuration for data generation pipeline."""

    template_dir: Path = Field(
        default=Path("awab_datagen/templates/library"),
        description="Directory containing YAML templates"
    )
    output_dir: Path = Field(
        default=Path("data/output"),
        description="Directory for output files"
    )
    personas_per_scenario: int = Field(
        default=3,
        description="Number of personas to generate per scenario"
    )
    single_turn_ratio: float = Field(
        default=0.6,
        description="Ratio of single-turn to multi-turn conversations"
    )
    llm_provider: str = Field(
        default="claude",
        description="LLM provider: 'claude' or 'openai'"
    )
    llm_api_key: str = Field(
        description="API key for LLM provider"
    )
    llm_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="LLM model to use"
    )

    class Config:
        """Pydantic config."""
        extra = "allow"
