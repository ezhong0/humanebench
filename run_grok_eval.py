"""Run evaluation for Grok 2 only."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from awab_evaluator.adapters import OpenRouterAdapter
from awab_evaluator.evaluation import LLMEvaluator
from awab_evaluator.runners import BenchmarkRunner
from awab_evaluator.reporting import HTMLReportGenerator

# Configuration
DATASET_PATH = Path("data/output/massive_combinatorial_dataset/dataset.jsonl")
OUTPUT_DIR = Path("data/evaluation_results")
MAX_TESTS = None

# Grok model
GROK_CONFIG = {
    "name": "Grok 3 Mini",
    "provider": "openrouter",
    "model": "x-ai/grok-3-mini",
}

# Evaluator configuration
EVALUATOR_PROVIDER = "openai"
EVALUATOR_MODEL = "gpt-4o-mini"

def main():
    print("\n" + "="*70)
    print("AWAB Grok 2 Evaluation")
    print("="*70)

    # Get API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY not found in .env")
        return

    if not openai_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    print(f"\n✓ Model: {GROK_CONFIG['name']}")
    print(f"✓ Dataset: {DATASET_PATH}")
    print(f"✓ Evaluator: {EVALUATOR_MODEL}\n")

    # Create evaluator
    from awab_evaluator.adapters import OpenAIAdapter
    evaluator_adapter = OpenAIAdapter(EVALUATOR_MODEL, openai_key)
    evaluator = LLMEvaluator(evaluator_adapter, EVALUATOR_MODEL)

    # Create Grok adapter
    grok_adapter = OpenRouterAdapter(GROK_CONFIG['model'], openrouter_key)

    # Run benchmark
    runner = BenchmarkRunner(evaluator, OUTPUT_DIR)
    results = runner.run_benchmark(
        ai_adapter=grok_adapter,
        dataset_path=DATASET_PATH,
        ai_system_name=GROK_CONFIG['name'],
        max_tests=MAX_TESTS,
    )

    # Generate HTML report
    report_gen = HTMLReportGenerator()
    report_path = OUTPUT_DIR / results.run_id / "report.html"
    report_gen.generate(results, report_path)

    print(f"\n✓ Report: {report_path}")
    print(f"\n✅ Grok 2 evaluation complete!")
    print(f"   Overall Score: {results.overall_score:.2f}/5.0")
    print(f"   Safety Pass Rate: {results.safety_pass_rate:.1f}%")
    print(f"   Critical Failures: {results.critical_failures}")

if __name__ == "__main__":
    main()
