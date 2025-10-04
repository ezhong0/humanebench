"""Run multi-model evaluation and create unified comparison report."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from awab_evaluator.adapters import OpenAIAdapter, OpenRouterAdapter
from awab_evaluator.evaluation import LLMEvaluator
from awab_evaluator.runners import BenchmarkRunner
from awab_evaluator.reporting import HTMLReportGenerator

# Configuration
DATASET_PATH = Path("data/output/unique_dataset/dataset.jsonl")
OUTPUT_DIR = Path("data/evaluation_results")
MAX_TESTS = None  # Test all examples (28 total)

# Affordable models to test
MODELS_TO_TEST = [
    {
        "name": "Gemini Flash 1.5",
        "provider": "openrouter",
        "model": "google/gemini-flash-1.5",
    },
    {
        "name": "Claude 3 Haiku",
        "provider": "openrouter",
        "model": "anthropic/claude-3-haiku",
    },
    {
        "name": "Llama 3 8B",
        "provider": "openrouter",
        "model": "meta-llama/llama-3-8b-instruct",
    },
    {
        "name": "Grok Beta",
        "provider": "openrouter",
        "model": "x-ai/grok-beta",
    },
    {
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "model": "gpt-3.5-turbo",
    },
]

# Evaluator configuration
EVALUATOR_PROVIDER = "openai"
EVALUATOR_MODEL = "gpt-4o-mini"

def create_adapter(provider, model, api_key):
    """Create appropriate adapter."""
    if provider == "openai":
        return OpenAIAdapter(model, api_key)
    elif provider == "openrouter":
        return OpenRouterAdapter(model, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def main():
    print("\n" + "="*70)
    print("AWAB Multi-Model Benchmark Evaluation")
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

    print(f"\n✓ Testing {len(MODELS_TO_TEST)} models")
    print(f"✓ Dataset: {DATASET_PATH}")
    print(f"✓ Tests per model: {MAX_TESTS}")
    print(f"✓ Evaluator: {EVALUATOR_MODEL}\n")

    # Create evaluator
    evaluator_key = openai_key if EVALUATOR_PROVIDER == "openai" else openrouter_key
    evaluator_adapter = create_adapter(EVALUATOR_PROVIDER, EVALUATOR_MODEL, evaluator_key)
    evaluator = LLMEvaluator(evaluator_adapter, EVALUATOR_MODEL)

    # Run evaluations
    all_results = []

    for i, model_config in enumerate(MODELS_TO_TEST):
        print(f"\n{'='*70}")
        print(f"[{i+1}/{len(MODELS_TO_TEST)}] Evaluating: {model_config['name']}")
        print(f"Provider: {model_config['provider']} | Model: {model_config['model']}")
        print(f"{'='*70}\n")

        try:
            # Get API key for this model
            if model_config['provider'] == 'openrouter':
                api_key = openrouter_key
            elif model_config['provider'] == 'openai':
                api_key = openai_key
            else:
                print(f"⚠️  Unknown provider, skipping...")
                continue

            # Create adapter
            adapter = create_adapter(model_config['provider'], model_config['model'], api_key)

            # Run benchmark
            runner = BenchmarkRunner(evaluator, OUTPUT_DIR)
            results = runner.run_benchmark(
                ai_adapter=adapter,
                dataset_path=DATASET_PATH,
                ai_system_name=model_config['name'],
                max_tests=MAX_TESTS,
            )

            all_results.append(results)

            # Generate individual HTML report
            report_gen = HTMLReportGenerator()
            report_path = OUTPUT_DIR / results.run_id / "report.html"
            report_gen.generate(results, report_path)
            print(f"\n✓ Report: {report_path}")

        except Exception as e:
            print(f"\n❌ Error evaluating {model_config['name']}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Generate comparison summary
    if all_results:
        print(f"\n{'='*70}")
        print("UNIFIED COMPARISON SUMMARY")
        print(f"{'='*70}\n")

        # Sort by overall score
        sorted_results = sorted(all_results, key=lambda r: r.overall_score, reverse=True)

        # Table header
        print(f"{'Rank':<6} {'Model':<25} {'Overall':<10} {'Safety':<10} {'Pass Rate':<12} {'Critical':<10}")
        print("-" * 75)

        # Table rows
        for rank, result in enumerate(sorted_results, 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(
                f"{emoji} {rank:<4} "
                f"{result.ai_system:<25} "
                f"{result.overall_score:<10.2f} "
                f"{result.safety_dignity_avg:<10.2f} "
                f"{result.safety_pass_rate:<11.1f}% "
                f"{result.critical_failures:<10}"
            )

        print(f"\n{'='*70}")
        print("Detailed Breakdown by Model")
        print(f"{'='*70}\n")

        for result in sorted_results:
            print(f"\n{result.ai_system}")
            print("-" * 40)
            print(f"  Overall Score:        {result.overall_score:.2f}/5.0")
            print(f"  Safety & Dignity:     {result.safety_dignity_avg:.2f}/5.0")
            print(f"  Long-term Wellbeing:  {result.longterm_wellbeing_avg:.2f}/5.0")
            print(f"  Transparency:         {result.transparency_avg:.2f}/5.0")
            print(f"  Safety Pass Rate:     {result.safety_pass_rate:.1f}%")
            print(f"  Critical Failures:    {result.critical_failures}")

        # Save comparison data
        import json
        comparison_file = OUTPUT_DIR / "multi_model_comparison.json"
        comparison_data = {
            "models": [
                {
                    "name": r.ai_system,
                    "overall_score": r.overall_score,
                    "safety_dignity": r.safety_dignity_avg,
                    "longterm_wellbeing": r.longterm_wellbeing_avg,
                    "transparency": r.transparency_avg,
                    "safety_pass_rate": r.safety_pass_rate,
                    "critical_failures": r.critical_failures,
                    "run_id": r.run_id,
                }
                for r in sorted_results
            ]
        }

        with open(comparison_file, 'w') as f:
            json.dump(comparison_data, f, indent=2)

        print(f"\n💾 Comparison data saved to: {comparison_file}")
        print(f"\n✅ All evaluations complete!")
        print(f"   Best performer: {sorted_results[0].ai_system} ({sorted_results[0].overall_score:.2f}/5.0)")

    else:
        print("\n⚠️  No results generated")

if __name__ == "__main__":
    main()
