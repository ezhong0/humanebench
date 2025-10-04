"""Benchmark test runner for evaluating AI systems."""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import uuid

from ..models import BenchmarkResults, EvaluationResult, AISystemConfig
from ..evaluation import LLMEvaluator
from ..adapters import BaseAIAdapter


class BenchmarkRunner:
    """Runs benchmark evaluations on AI systems."""

    def __init__(
        self,
        evaluator: LLMEvaluator,
        output_dir: Path = Path("data/evaluation_results")
    ):
        """
        Initialize benchmark runner.

        Args:
            evaluator: LLM evaluator instance
            output_dir: Directory to save results
        """
        self.evaluator = evaluator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_benchmark(
        self,
        ai_adapter: BaseAIAdapter,
        dataset_path: Path,
        ai_system_name: str,
        max_tests: int = None,
        system_prompt: str = None,
    ) -> BenchmarkResults:
        """
        Run full benchmark on an AI system.

        Args:
            ai_adapter: Adapter for AI system to test
            dataset_path: Path to JSONL dataset file
            ai_system_name: Name of AI system being tested
            max_tests: Maximum number of tests to run (None for all)
            system_prompt: Optional system prompt for AI

        Returns:
            BenchmarkResults with aggregated scores
        """
        run_id = f"{ai_system_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*60}")
        print(f"Running AWAB Benchmark: {ai_system_name}")
        print(f"Run ID: {run_id}")
        print(f"{'='*60}\n")

        # Load dataset
        test_cases = self._load_dataset(dataset_path, max_tests)
        print(f"✓ Loaded {len(test_cases)} test cases\n")

        # Run tests
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"[{i+1}/{len(test_cases)}] Testing: {test_case['id']} ({test_case['domain']})")

            try:
                result = self._run_single_test(
                    ai_adapter,
                    test_case,
                    ai_system_name,
                    system_prompt
                )
                results.append(result)

                # Print quick summary
                score = result.scores.overall_score
                flag = "⚠️  UNSAFE" if result.safety_flag else "✓ SAFE"
                print(f"   Score: {score:.2f}/5.0 | {flag}")

            except Exception as e:
                print(f"   ✗ Error: {e}")
                continue

        # Aggregate results
        print(f"\n{'='*60}")
        print("Aggregating results...")
        benchmark_results = self._aggregate_results(
            run_id,
            ai_system_name,
            dataset_path.stem,
            results
        )

        # Save results
        self._save_results(run_id, benchmark_results)

        print(f"\n✅ Benchmark complete!")
        print(f"   Overall Score: {benchmark_results.overall_score:.2f}/5.0")
        print(f"   Safety Pass Rate: {benchmark_results.safety_pass_rate:.1f}%")
        print(f"   Critical Failures: {benchmark_results.critical_failures}")
        print(f"\n   Results saved to: {self.output_dir / run_id}")

        return benchmark_results

    def _run_single_test(
        self,
        ai_adapter: BaseAIAdapter,
        test_case: Dict,
        ai_system_name: str,
        system_prompt: str = None,
    ) -> EvaluationResult:
        """Run a single test case."""

        # Extract user messages from conversation
        user_messages = [
            turn["content"] for turn in test_case["conversation"]
            if turn["role"] == "user"
        ]

        # Get AI response
        ai_response, response_time_ms, tokens_used = ai_adapter.test_response(
            user_messages,
            system_prompt
        )

        # Extract required actions from test case
        required_actions = []
        if test_case.get("metadata", {}).get("required_actions"):
            required_actions = test_case["metadata"]["required_actions"]
        elif test_case.get("required_ground_truth", {}).get("required_actions"):
            required_actions = test_case["required_ground_truth"]["required_actions"]

        # Evaluate response
        result = self.evaluator.evaluate(
            test_id=test_case["id"],
            ai_system=ai_system_name,
            domain=test_case["domain"],
            harm_pattern=test_case["harm_pattern"],
            vulnerability_level=test_case["vulnerability_level"],
            scenario_description=test_case.get("metadata", {}).get("scenario_description", ""),
            user_messages=user_messages,
            ai_response=ai_response,
            required_actions=required_actions,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
        )

        return result

    def _load_dataset(self, dataset_path: Path, max_tests: int = None) -> List[Dict]:
        """Load test cases from JSONL file."""
        test_cases = []

        with open(dataset_path, 'r') as f:
            for line in f:
                if max_tests and len(test_cases) >= max_tests:
                    break
                test_cases.append(json.loads(line))

        return test_cases

    def _aggregate_results(
        self,
        run_id: str,
        ai_system: str,
        dataset_name: str,
        results: List[EvaluationResult]
    ) -> BenchmarkResults:
        """Aggregate individual results into benchmark summary."""

        total_tests = len(results)

        if total_tests == 0:
            # No results - return zero scores
            return BenchmarkResults(
                run_id=run_id,
                ai_system=ai_system,
                dataset_name=dataset_name,
                total_tests=0,
                overall_score=0.0,
                safety_dignity_avg=0.0,
                longterm_wellbeing_avg=0.0,
                transparency_avg=0.0,
                safety_pass_rate=0.0,
                critical_failures=0,
                results_by_domain={},
                results_by_pattern={},
                results_by_vulnerability={},
                individual_results=[],
            )

        # Calculate average scores
        safety_dignity_avg = sum(r.scores.safety_dignity for r in results) / total_tests
        longterm_wellbeing_avg = sum(r.scores.longterm_wellbeing for r in results) / total_tests
        transparency_avg = sum(r.scores.transparency for r in results) / total_tests
        overall_score = sum(r.scores.overall_score for r in results) / total_tests

        # Safety metrics
        safe_tests = sum(1 for r in results if not r.safety_flag)
        safety_pass_rate = (safe_tests / total_tests) * 100

        # Critical failures (high vulnerability tests that failed)
        critical_failures = sum(
            1 for r in results
            if r.vulnerability_level == "high" and r.safety_flag
        )

        # Breakdown by domain
        results_by_domain = self._breakdown_by_field(results, "domain")
        results_by_pattern = self._breakdown_by_field(results, "harm_pattern")
        results_by_vulnerability = self._breakdown_by_field(results, "vulnerability_level")

        return BenchmarkResults(
            run_id=run_id,
            ai_system=ai_system,
            dataset_name=dataset_name,
            total_tests=total_tests,
            overall_score=overall_score,
            safety_dignity_avg=safety_dignity_avg,
            longterm_wellbeing_avg=longterm_wellbeing_avg,
            transparency_avg=transparency_avg,
            safety_pass_rate=safety_pass_rate,
            critical_failures=critical_failures,
            results_by_domain=results_by_domain,
            results_by_pattern=results_by_pattern,
            results_by_vulnerability=results_by_vulnerability,
            individual_results=results,
        )

    def _breakdown_by_field(self, results: List[EvaluationResult], field: str) -> Dict:
        """Calculate breakdown statistics by a field."""
        breakdown = {}

        # Group results by field value
        grouped = {}
        for result in results:
            value = getattr(result, field)
            if value not in grouped:
                grouped[value] = []
            grouped[value].append(result)

        # Calculate stats for each group
        for value, group_results in grouped.items():
            breakdown[value] = {
                "count": len(group_results),
                "avg_score": sum(r.scores.overall_score for r in group_results) / len(group_results),
                "safety_pass_rate": (sum(1 for r in group_results if not r.safety_flag) / len(group_results)) * 100,
                "avg_safety_dignity": sum(r.scores.safety_dignity for r in group_results) / len(group_results),
                "avg_longterm_wellbeing": sum(r.scores.longterm_wellbeing for r in group_results) / len(group_results),
                "avg_transparency": sum(r.scores.transparency for r in group_results) / len(group_results),
            }

        return breakdown

    def _save_results(self, run_id: str, results: BenchmarkResults):
        """Save results to disk."""
        run_dir = self.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save full results as JSON
        results_file = run_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(results.model_dump(), f, indent=2, default=str)

        # Save summary
        summary_file = run_dir / "summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"AWAB Benchmark Results\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"AI System: {results.ai_system}\n")
            f.write(f"Run ID: {results.run_id}\n")
            f.write(f"Dataset: {results.dataset_name}\n")
            f.write(f"Total Tests: {results.total_tests}\n\n")
            f.write(f"Overall Score: {results.overall_score:.2f}/5.0\n")
            f.write(f"Safety Pass Rate: {results.safety_pass_rate:.1f}%\n")
            f.write(f"Critical Failures: {results.critical_failures}\n\n")
            f.write(f"Dimension Scores:\n")
            f.write(f"  Safety & Dignity: {results.safety_dignity_avg:.2f}/5.0\n")
            f.write(f"  Long-term Wellbeing: {results.longterm_wellbeing_avg:.2f}/5.0\n")
            f.write(f"  Transparency: {results.transparency_avg:.2f}/5.0\n")
