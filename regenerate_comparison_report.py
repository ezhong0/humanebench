"""Regenerate the comprehensive multi-model comparison HTML report."""

import json
from pathlib import Path
from awab_evaluator.reporting.multi_model_comparison_html_lite import MultiModelComparisonHTMLGeneratorLite
from awab_evaluator.models import BenchmarkResults, EvaluationResult, EvaluationScore

def load_results_from_json(results_dir: Path):
    """Load all results.json files and convert to BenchmarkResults objects."""
    all_results = []

    for results_file in results_dir.glob("*/results.json"):
        with open(results_file) as f:
            data = json.load(f)

            # Convert individual results
            individual_results = []
            for result_data in data.get('individual_results', []):
                scores = EvaluationScore(
                    safety_dignity=result_data['scores']['safety_dignity'],
                    longterm_wellbeing=result_data['scores']['longterm_wellbeing'],
                    transparency=result_data['scores']['transparency']
                )

                eval_result = EvaluationResult(
                    test_id=result_data['test_id'],
                    ai_system=data['ai_system'],
                    domain=result_data.get('domain', ''),
                    harm_pattern=result_data.get('harm_pattern', ''),
                    vulnerability_level=result_data.get('vulnerability_level', ''),
                    user_messages=result_data['user_messages'],
                    ai_response=result_data['ai_response'],
                    scores=scores,
                    evaluator_reasoning=result_data.get('evaluator_reasoning', ''),
                    safety_flag=result_data.get('safety_flag', False)
                )
                individual_results.append(eval_result)

            # Create BenchmarkResults object
            benchmark_result = BenchmarkResults(
                run_id=data.get('run_id', ''),
                ai_system=data['ai_system'],
                dataset_name=data['dataset_name'],
                total_tests=data['total_tests'],
                overall_score=data['overall_score'],
                safety_dignity_avg=data['safety_dignity_avg'],
                longterm_wellbeing_avg=data['longterm_wellbeing_avg'],
                transparency_avg=data['transparency_avg'],
                safety_pass_rate=data['safety_pass_rate'],
                critical_failures=data['critical_failures'],
                individual_results=individual_results,
                results_by_domain=data.get('results_by_domain', {}),
                results_by_pattern=data.get('results_by_pattern', {}),
                results_by_vulnerability=data.get('results_by_vulnerability', {})
            )

            all_results.append(benchmark_result)

    return all_results

def main():
    print("\n" + "="*70)
    print("Regenerating Multi-Model Comparison Report")
    print("="*70 + "\n")

    results_dir = Path("data/evaluation_results")
    output_path = results_dir / "comprehensive_multi_model_comparison.html"

    print(f"Loading results from: {results_dir}")
    all_results = load_results_from_json(results_dir)

    print(f"Found {len(all_results)} model evaluations:")
    for r in all_results:
        print(f"  - {r.ai_system}: {r.overall_score:.2f}/5.0")

    print(f"\nGenerating report...")
    generator = MultiModelComparisonHTMLGeneratorLite()
    generator.generate(all_results, output_path)

    print(f"\n✅ Report generated: {output_path}")
    print(f"\nOpening report in browser...")

    import subprocess
    subprocess.run(["open", str(output_path)])

if __name__ == "__main__":
    main()
