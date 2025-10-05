"""Main pipeline orchestrator for AWAB data generation."""

from pathlib import Path
from typing import List
import json
from ..core.models import DataPoint
from ..core.config import PipelineConfig
from ..templates.manager import TemplateManager
from ..generation.personas import PersonaGenerator
from ..generation.conversations import ConversationGenerator
from ..generation.llm import LLMClient


class DataGenerationPipeline:
    """Orchestrates the full data generation pipeline."""

    def __init__(self, config: PipelineConfig, llm_client: LLMClient):
        """
        Initialize pipeline.

        Args:
            config: Pipeline configuration
            llm_client: LLM client for conversation generation
        """
        self.config = config
        self.template_manager = TemplateManager(config.template_dir)
        self.persona_gen = PersonaGenerator()
        self.conversation_gen = ConversationGenerator(llm_client)

    def run(self, generate_ai_responses: bool = False) -> List[DataPoint]:
        """
        Execute full pipeline.

        Args:
            generate_ai_responses: If True, generate AI responses using LLM

        Returns:
            List of generated data points
        """
        print("🚀 Starting AWAB data generation pipeline...")

        # Stage 1: Load templates
        scenarios = self.template_manager.get_scenario_matrix()
        print(f"✓ Loaded {len(scenarios)} scenario templates")

        if len(scenarios) == 0:
            print("⚠️  No templates found. Creating sample templates...")
            print(f"   Please add YAML templates to: {self.config.template_dir}")
            return []

        # Show template stats
        stats = self.template_manager.get_stats()
        print(f"  • By domain: {stats['by_domain']}")
        print(f"  • By pattern: {stats['by_pattern']}")
        print(f"  • By vulnerability: {stats['by_vulnerability']}")

        # Stage 2: Generate dataset
        datapoints = []
        for i, scenario in enumerate(scenarios):
            print(f"\n[{i+1}/{len(scenarios)}] Processing: {scenario.id}")
            print(f"  Domain: {scenario.domain.value} | Pattern: {scenario.harm_pattern.value} | Level: {scenario.vulnerability_level.value}")

            # Generate one datapoint per template variant with unique personas
            num_templates = len(scenario.user_message_templates)
            print(f"  ✓ {num_templates} template variants")

            # Generate unique personas for each template variant
            unique_personas = self.persona_gen.generate(scenario, n=num_templates, ensure_diversity=True)

            # Generate conversations for each template variant
            for j in range(num_templates):
                # Use a unique persona for each template variant
                unique_persona = unique_personas[j]

                conversation = self.conversation_gen.generate(
                    scenario,
                    unique_persona,
                    generate_ai_responses=generate_ai_responses,
                    template_index=j  # Use each template exactly once
                )

                datapoint = DataPoint(
                    id=f"awab_{len(datapoints):04d}",
                    domain=scenario.domain,
                    harm_pattern=scenario.harm_pattern,
                    vulnerability_level=scenario.vulnerability_level,
                    persona=unique_persona,
                    conversation=conversation,
                    metadata={
                        "scenario_id": scenario.id,
                        "scenario_description": scenario.description,
                        "conversation_type": scenario.conversation_type,
                        "template_index": j,
                    }
                )
                datapoints.append(datapoint)

            print(f"  ✓ Generated {num_templates} unique conversations with diverse personas")

        print(f"\n✅ Generated {len(datapoints)} total conversations")

        # Stage 3: Export
        self._export(datapoints)
        self._export_stats(datapoints)

        return datapoints

    def _export(self, datapoints: List[DataPoint]):
        """Export datapoints to JSONL."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.config.output_dir / "dataset.jsonl"

        with open(output_path, 'w') as f:
            for dp in datapoints:
                f.write(dp.model_dump_json() + '\n')

        print(f"\n💾 Exported to: {output_path}")

    def _export_stats(self, datapoints: List[DataPoint]):
        """Export dataset statistics."""
        stats = {
            "total": len(datapoints),
            "by_domain": {},
            "by_pattern": {},
            "by_vulnerability": {},
            "conversation_types": {},
        }

        for dp in datapoints:
            # Count by domain
            domain = dp.domain.value
            stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1

            # Count by pattern
            pattern = dp.harm_pattern.value
            stats["by_pattern"][pattern] = stats["by_pattern"].get(pattern, 0) + 1

            # Count by vulnerability
            vuln = dp.vulnerability_level.value
            stats["by_vulnerability"][vuln] = stats["by_vulnerability"].get(vuln, 0) + 1

            # Count conversation types
            conv_type = dp.metadata.get("conversation_type", "unknown")
            stats["conversation_types"][conv_type] = stats["conversation_types"].get(conv_type, 0) + 1

        # Write stats
        stats_path = self.config.output_dir / "dataset_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"📊 Stats exported to: {stats_path}")
        print(f"\nDataset Summary:")
        print(f"  • Total conversations: {stats['total']}")
        print(f"  • Domains: {stats['by_domain']}")
        print(f"  • Patterns: {stats['by_pattern']}")
        print(f"  • Vulnerability levels: {stats['by_vulnerability']}")
