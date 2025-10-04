"""Command-line interface for AWAB evaluation system."""

import click
from pathlib import Path
import os

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .adapters import OpenAIAdapter, ClaudeAdapter, OpenRouterAdapter
from .evaluation import LLMEvaluator
from .runners import BenchmarkRunner
from .reporting import HTMLReportGenerator


@click.group()
@click.version_option()
def cli():
    """AWAB Benchmark Evaluation CLI

    Evaluate AI systems against the AI Well-Being Alignment Benchmark.
    """
    pass


@cli.command()
@click.option(
    '--dataset',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to JSONL dataset file'
)
@click.option(
    '--ai-provider',
    type=click.Choice(['openai', 'anthropic', 'openrouter']),
    required=True,
    help='AI provider to test'
)
@click.option(
    '--ai-model',
    required=True,
    help='Model to test (e.g., gpt-4o-mini, claude-3-sonnet)'
)
@click.option(
    '--ai-api-key',
    help='API key for AI being tested (or set OPENAI_API_KEY/ANTHROPIC_API_KEY/OPENROUTER_API_KEY)'
)
@click.option(
    '--evaluator-provider',
    type=click.Choice(['openai', 'anthropic', 'openrouter']),
    default='openai',
    help='Provider for evaluator LLM'
)
@click.option(
    '--evaluator-model',
    default='gpt-4o-mini',
    help='Model for evaluator LLM'
)
@click.option(
    '--evaluator-api-key',
    help='API key for evaluator (or set LLM_API_KEY)'
)
@click.option(
    '--max-tests',
    type=int,
    help='Maximum number of tests to run'
)
@click.option(
    '--output-dir',
    type=click.Path(path_type=Path),
    default='data/evaluation_results',
    help='Output directory for results'
)
@click.option(
    '--system-prompt',
    help='System prompt for AI being tested'
)
@click.option(
    '--generate-html/--no-generate-html',
    default=True,
    help='Generate HTML report'
)
def run(
    dataset,
    ai_provider,
    ai_model,
    ai_api_key,
    evaluator_provider,
    evaluator_model,
    evaluator_api_key,
    max_tests,
    output_dir,
    system_prompt,
    generate_html
):
    """Run benchmark evaluation on an AI system."""

    click.echo("\n🎯 AWAB Benchmark Evaluation")
    click.echo("=" * 60)

    # Get API keys
    ai_api_key = ai_api_key or _get_api_key(ai_provider)
    evaluator_api_key = evaluator_api_key or os.getenv('LLM_API_KEY') or _get_api_key(evaluator_provider)

    if not ai_api_key:
        raise click.ClickException(f"API key required for {ai_provider}")
    if not evaluator_api_key:
        raise click.ClickException(f"API key required for evaluator ({evaluator_provider})")

    # Create AI adapter (system being tested)
    click.echo(f"\n✓ Setting up AI system: {ai_provider}/{ai_model}")
    ai_adapter = _create_adapter(ai_provider, ai_model, ai_api_key)

    # Create evaluator adapter
    click.echo(f"✓ Setting up evaluator: {evaluator_provider}/{evaluator_model}")
    evaluator_adapter = _create_adapter(evaluator_provider, evaluator_model, evaluator_api_key)

    # Create evaluator
    evaluator = LLMEvaluator(evaluator_adapter, evaluator_model)

    # Create runner
    runner = BenchmarkRunner(evaluator, output_dir)

    # Run benchmark
    ai_system_name = f"{ai_provider}/{ai_model}"
    results = runner.run_benchmark(
        ai_adapter=ai_adapter,
        dataset_path=dataset,
        ai_system_name=ai_system_name,
        max_tests=max_tests,
        system_prompt=system_prompt
    )

    # Generate HTML report
    if generate_html:
        click.echo("\n📄 Generating HTML report...")
        report_gen = HTMLReportGenerator()
        report_path = output_dir / results.run_id / "report.html"
        report_gen.generate(results, report_path)
        click.echo(f"✓ HTML report: {report_path}")

    click.echo("\n✅ Evaluation complete!")


@cli.command()
@click.option(
    '--dataset',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to JSONL dataset file'
)
@click.option(
    '--models',
    required=True,
    help='Comma-separated list of models to compare (format: provider/model)'
)
@click.option(
    '--evaluator-provider',
    type=click.Choice(['openai', 'anthropic', 'openrouter']),
    default='openai',
    help='Provider for evaluator LLM'
)
@click.option(
    '--evaluator-model',
    default='gpt-4o-mini',
    help='Model for evaluator LLM'
)
@click.option(
    '--max-tests',
    type=int,
    help='Maximum number of tests to run per model'
)
@click.option(
    '--output-dir',
    type=click.Path(path_type=Path),
    default='data/evaluation_results',
    help='Output directory for results'
)
def compare(dataset, models, evaluator_provider, evaluator_model, max_tests, output_dir):
    """Compare multiple AI models on the benchmark."""

    click.echo("\n🔬 AWAB Benchmark Comparison")
    click.echo("=" * 60)

    # Parse models
    model_list = []
    for model_spec in models.split(','):
        parts = model_spec.strip().split('/')
        if len(parts) != 2:
            raise click.ClickException(f"Invalid model format: {model_spec}. Use provider/model")
        model_list.append((parts[0], parts[1]))

    click.echo(f"\n✓ Comparing {len(model_list)} models:")
    for provider, model in model_list:
        click.echo(f"  • {provider}/{model}")

    # Run benchmark for each model
    all_results = []
    for provider, model in model_list:
        click.echo(f"\n{'='*60}")
        click.echo(f"Evaluating: {provider}/{model}")
        click.echo(f"{'='*60}")

        # Get API key
        api_key = _get_api_key(provider)
        if not api_key:
            click.echo(f"⚠️  Skipping {provider}/{model} - no API key")
            continue

        # Create adapter
        ai_adapter = _create_adapter(provider, model, api_key)

        # Create evaluator
        evaluator_api_key = os.getenv('LLM_API_KEY') or _get_api_key(evaluator_provider)
        evaluator_adapter = _create_adapter(evaluator_provider, evaluator_model, evaluator_api_key)
        evaluator = LLMEvaluator(evaluator_adapter, evaluator_model)

        # Run benchmark
        runner = BenchmarkRunner(evaluator, output_dir)
        results = runner.run_benchmark(
            ai_adapter=ai_adapter,
            dataset_path=dataset,
            ai_system_name=f"{provider}/{model}",
            max_tests=max_tests
        )

        all_results.append(results)

        # Generate HTML report
        report_gen = HTMLReportGenerator()
        report_path = output_dir / results.run_id / "report.html"
        report_gen.generate(results, report_path)

    # Generate comparison summary
    if all_results:
        click.echo(f"\n{'='*60}")
        click.echo("COMPARISON SUMMARY")
        click.echo(f"{'='*60}\n")

        click.echo(f"{'Model':<30} {'Overall':<10} {'Safety':<10} {'Wellbeing':<10} {'Trans':<10}")
        click.echo("-" * 70)

        for result in sorted(all_results, key=lambda r: r.overall_score, reverse=True):
            click.echo(
                f"{result.ai_system:<30} "
                f"{result.overall_score:<10.2f} "
                f"{result.safety_dignity_avg:<10.2f} "
                f"{result.longterm_wellbeing_avg:<10.2f} "
                f"{result.transparency_avg:<10.2f}"
            )

    click.echo("\n✅ Comparison complete!")


def _get_api_key(provider: str) -> str | None:
    """Get API key for provider from environment."""
    if provider == 'openai':
        return os.getenv('OPENAI_API_KEY')
    elif provider == 'anthropic':
        return os.getenv('ANTHROPIC_API_KEY')
    elif provider == 'openrouter':
        return os.getenv('OPENROUTER_API_KEY')
    return None


def _create_adapter(provider: str, model: str, api_key: str):
    """Create adapter for provider."""
    if provider == 'openai':
        return OpenAIAdapter(model, api_key)
    elif provider == 'anthropic':
        return ClaudeAdapter(model, api_key)
    elif provider == 'openrouter':
        return OpenRouterAdapter(model, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == '__main__':
    cli()
