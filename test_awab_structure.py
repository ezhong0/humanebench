"""
Quick test to verify AWAB data generation system structure.

Run this after installing dependencies:
  pip install pydantic click pyyaml jinja2
"""

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from awab_datagen import (
            Domain,
            HarmPattern,
            VulnerabilityLevel,
            Persona,
            DataPoint,
            PipelineConfig,
            DataGenerationPipeline,
        )
        print("✓ Core imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    try:
        from awab_datagen.generation import (
            PersonaGenerator,
            ConversationGenerator,
            MockLLMClient,
        )
        print("✓ Generation imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    try:
        from awab_datagen.templates import TemplateManager
        print("✓ Template manager import successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    return True


def test_template_loading():
    """Test loading templates."""
    print("\nTesting template loading...")

    try:
        from pathlib import Path
        from awab_datagen.templates import TemplateManager

        template_dir = Path("awab_datagen/templates/library")
        manager = TemplateManager(template_dir)

        stats = manager.get_stats()
        print(f"✓ Loaded {stats['total']} templates")
        print(f"  • By domain: {stats['by_domain']}")
        print(f"  • By pattern: {stats['by_pattern']}")
        print(f"  • By vulnerability: {stats['by_vulnerability']}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_persona_generation():
    """Test persona generation."""
    print("\nTesting persona generation...")

    try:
        from awab_datagen.generation import PersonaGenerator
        from awab_datagen.templates import TemplateManager
        from pathlib import Path

        gen = PersonaGenerator(seed=42)

        # Get a sample scenario
        manager = TemplateManager(Path("awab_datagen/templates/library"))
        templates = manager.get_scenario_matrix()

        if templates:
            personas = gen.generate(templates[0], n=3)
            print(f"✓ Generated {len(personas)} personas")
            for i, p in enumerate(personas):
                print(f"  {i+1}. {p.to_description()}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_mock_generation():
    """Test full pipeline with mock LLM."""
    print("\nTesting mock data generation...")

    try:
        from pathlib import Path
        from awab_datagen import PipelineConfig, DataGenerationPipeline
        from awab_datagen.generation import MockLLMClient

        config = PipelineConfig(
            template_dir=Path("awab_datagen/templates/library"),
            output_dir=Path("data/output/test"),
            personas_per_scenario=2,
            llm_provider="mock",
            llm_api_key="mock"
        )

        llm_client = MockLLMClient()
        pipeline = DataGenerationPipeline(config, llm_client)

        datapoints = pipeline.run(generate_ai_responses=False)

        print(f"\n✓ Generated {len(datapoints)} datapoints")

        if datapoints:
            sample = datapoints[0]
            print(f"\nSample datapoint:")
            print(f"  ID: {sample.id}")
            print(f"  Domain: {sample.domain.value}")
            print(f"  Pattern: {sample.harm_pattern.value}")
            print(f"  Vulnerability: {sample.vulnerability_level.value}")
            print(f"  Persona: {sample.persona.to_description()}")
            print(f"  Conversation turns: {len(sample.conversation)}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("AWAB Data Generation System - Structure Test")
    print("=" * 60)

    # Run tests
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Template Loading", test_template_loading()))
    results.append(("Persona Generation", test_persona_generation()))
    results.append(("Mock Generation", test_mock_generation()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Generate data: python -m awab_datagen.cli generate --provider mock")
        print("  3. View stats: python -m awab_datagen.cli stats")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
