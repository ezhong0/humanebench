"""Template manager for loading and accessing scenario templates."""

import yaml
from pathlib import Path
from typing import List
from ..core.models import ScenarioTemplate, Domain, HarmPattern, VulnerabilityLevel


class TemplateManager:
    """Manages loading and accessing scenario templates."""

    def __init__(self, template_dir: Path):
        """
        Initialize template manager.

        Args:
            template_dir: Directory containing YAML template files
        """
        self.template_dir = Path(template_dir)
        self._templates: List[ScenarioTemplate] = []
        self._load_all()

    def _load_all(self):
        """Load all YAML templates from library."""
        if not self.template_dir.exists():
            print(f"Warning: Template directory {self.template_dir} does not exist")
            return

        yaml_files = list(self.template_dir.rglob("*.yaml")) + list(self.template_dir.rglob("*.yml"))

        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    docs = yaml.safe_load_all(f)
                    for doc in docs:
                        if doc:  # Skip empty documents
                            template = ScenarioTemplate(**doc)
                            self._templates.append(template)
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

    def get_by_domain(self, domain: Domain) -> List[ScenarioTemplate]:
        """Get all templates for a specific domain."""
        return [t for t in self._templates if t.domain == domain]

    def get_by_pattern(self, pattern: HarmPattern) -> List[ScenarioTemplate]:
        """Get all templates for a specific harm pattern."""
        return [t for t in self._templates if t.harm_pattern == pattern]

    def get_by_vulnerability(self, level: VulnerabilityLevel) -> List[ScenarioTemplate]:
        """Get all templates for a specific vulnerability level."""
        return [t for t in self._templates if t.vulnerability_level == level]

    def get_scenario_matrix(self) -> List[ScenarioTemplate]:
        """Get all scenarios for the full matrix (8×4×3)."""
        return self._templates

    def get_template(self, template_id: str) -> ScenarioTemplate | None:
        """Get a specific template by ID."""
        return next((t for t in self._templates if t.id == template_id), None)

    def get_stats(self) -> dict:
        """Get statistics about loaded templates."""
        return {
            "total": len(self._templates),
            "by_domain": {
                domain.value: len(self.get_by_domain(domain))
                for domain in Domain
            },
            "by_pattern": {
                pattern.value: len(self.get_by_pattern(pattern))
                for pattern in HarmPattern
            },
            "by_vulnerability": {
                level.value: len(self.get_by_vulnerability(level))
                for level in VulnerabilityLevel
            },
        }
