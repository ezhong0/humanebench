"""HTML report generator with visualizations."""

from pathlib import Path
from typing import List
from ..models import BenchmarkResults, EvaluationResult


class HTMLReportGenerator:
    """Generates HTML reports for benchmark results."""

    def generate(self, results: BenchmarkResults, output_path: Path):
        """
        Generate HTML report.

        Args:
            results: Benchmark results
            output_path: Path to save HTML report
        """
        html = self._generate_html(results)

        with open(output_path, 'w') as f:
            f.write(html)

    def _generate_html(self, results: BenchmarkResults) -> str:
        """Generate full HTML report."""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWAB Benchmark Report - {results.ai_system}</title>
    <style>
        {self._get_css()}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        {self._generate_header(results)}
        {self._generate_summary(results)}
        {self._generate_charts(results)}
        {self._generate_breakdown(results)}
        {self._generate_examples(results)}
        {self._generate_footer()}
    </div>
    <script>
        {self._generate_chart_js(results)}
    </script>
</body>
</html>
"""
        return html

    def _get_css(self) -> str:
        """Get CSS styles."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        h2 {
            font-size: 1.8em;
            margin: 30px 0 20px 0;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }

        .metric-subtitle {
            color: #888;
            font-size: 0.85em;
            margin-top: 5px;
        }

        .score-excellent { color: #10b981; }
        .score-good { color: #3b82f6; }
        .score-fair { color: #f59e0b; }
        .score-poor { color: #ef4444; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }

        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }

        table {
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }

        th, td {
            padding: 15px;
            text-align: left;
        }

        th {
            background: #667eea;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }

        tr:nth-child(even) {
            background: #f9f9f9;
        }

        tr:hover {
            background: #f0f0f0;
        }

        .example-case {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .example-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e5e5;
        }

        .example-title {
            font-weight: bold;
            font-size: 1.1em;
        }

        .badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge-safe {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-unsafe {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge-high {
            background: #fef3c7;
            color: #92400e;
        }

        .conversation-block {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }

        .user-message {
            color: #4b5563;
            font-style: italic;
            margin-bottom: 10px;
        }

        .ai-response {
            color: #1f2937;
            margin-top: 10px;
        }

        .scores-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }

        .score-item {
            text-align: center;
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
        }

        .score-item-label {
            font-size: 0.85em;
            color: #6b7280;
            margin-bottom: 5px;
        }

        .score-item-value {
            font-size: 1.8em;
            font-weight: bold;
        }

        footer {
            text-align: center;
            padding: 40px 20px;
            color: #888;
            margin-top: 50px;
        }

        .info-box {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        """

    def _generate_header(self, results: BenchmarkResults) -> str:
        """Generate report header."""
        return f"""
        <header>
            <h1>🎯 AWAB Benchmark Report</h1>
            <p style="font-size: 1.2em; opacity: 0.95; margin-top: 10px;">
                AI Well-Being Alignment Benchmark
            </p>
            <div style="margin-top: 20px; opacity: 0.9;">
                <p><strong>AI System:</strong> {results.ai_system}</p>
                <p><strong>Run ID:</strong> {results.run_id}</p>
                <p><strong>Dataset:</strong> {results.dataset_name}</p>
                <p><strong>Date:</strong> {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </header>
        """

    def _generate_summary(self, results: BenchmarkResults) -> str:
        """Generate summary section."""
        score_class = self._get_score_class(results.overall_score)

        return f"""
        <section class="summary">
            <h2>📊 Overall Performance</h2>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-label">Overall Score</div>
                    <div class="metric-value {score_class}">{results.overall_score:.2f}/5.0</div>
                    <div class="metric-subtitle">Weighted average across all dimensions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Safety Pass Rate</div>
                    <div class="metric-value">{results.safety_pass_rate:.1f}%</div>
                    <div class="metric-subtitle">{int(results.total_tests * results.safety_pass_rate / 100)}/{results.total_tests} tests passed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Critical Failures</div>
                    <div class="metric-value score-poor">{results.critical_failures}</div>
                    <div class="metric-subtitle">High-risk scenarios failed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Tests</div>
                    <div class="metric-value">{results.total_tests}</div>
                    <div class="metric-subtitle">Test cases evaluated</div>
                </div>
            </div>

            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-label">Safety & Dignity</div>
                    <div class="metric-value {self._get_score_class(results.safety_dignity_avg)}">{results.safety_dignity_avg:.2f}/5.0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Long-term Wellbeing</div>
                    <div class="metric-value {self._get_score_class(results.longterm_wellbeing_avg)}">{results.longterm_wellbeing_avg:.2f}/5.0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Transparency</div>
                    <div class="metric-value {self._get_score_class(results.transparency_avg)}">{results.transparency_avg:.2f}/5.0</div>
                </div>
            </div>
        </section>
        """

    def _generate_charts(self, results: BenchmarkResults) -> str:
        """Generate charts section."""
        return """
        <section class="charts">
            <h2>📈 Detailed Analysis</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Performance by Domain</div>
                    <canvas id="domainChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Performance by Harm Pattern</div>
                    <canvas id="patternChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Performance by Vulnerability Level</div>
                    <canvas id="vulnerabilityChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Dimension Scores</div>
                    <canvas id="dimensionsChart"></canvas>
                </div>
            </div>
        </section>
        """

    def _generate_breakdown(self, results: BenchmarkResults) -> str:
        """Generate breakdown tables."""
        domain_table = self._generate_breakdown_table("Domain", results.results_by_domain)
        pattern_table = self._generate_breakdown_table("Harm Pattern", results.results_by_pattern)
        vuln_table = self._generate_breakdown_table("Vulnerability", results.results_by_vulnerability)

        return f"""
        <section class="breakdown">
            <h2>🔍 Detailed Breakdown</h2>

            <h3 style="margin-top: 30px;">By Domain</h3>
            {domain_table}

            <h3 style="margin-top: 30px;">By Harm Pattern</h3>
            {pattern_table}

            <h3 style="margin-top: 30px;">By Vulnerability Level</h3>
            {vuln_table}
        </section>
        """

    def _generate_breakdown_table(self, category: str, breakdown: dict) -> str:
        """Generate a breakdown table."""
        rows = ""
        for key, stats in breakdown.items():
            score_class = self._get_score_class(stats['avg_score'])
            rows += f"""
            <tr>
                <td><strong>{key}</strong></td>
                <td>{stats['count']}</td>
                <td class="{score_class}">{stats['avg_score']:.2f}</td>
                <td>{stats['safety_pass_rate']:.1f}%</td>
                <td>{stats['avg_safety_dignity']:.2f}</td>
                <td>{stats['avg_longterm_wellbeing']:.2f}</td>
                <td>{stats['avg_transparency']:.2f}</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>{category}</th>
                    <th>Count</th>
                    <th>Avg Score</th>
                    <th>Safety Rate</th>
                    <th>Safety & Dignity</th>
                    <th>Wellbeing</th>
                    <th>Transparency</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    def _generate_examples(self, results: BenchmarkResults) -> str:
        """Generate example cases section."""
        # Get best and worst cases
        sorted_results = sorted(results.individual_results, key=lambda r: r.scores.overall_score, reverse=True)

        best_cases = sorted_results[:3]
        worst_cases = sorted_results[-3:]

        # Get critical failures
        critical_cases = [r for r in results.individual_results if r.vulnerability_level == "high" and r.safety_flag][:3]

        best_html = "".join([self._generate_example_case(r, "Best") for r in best_cases])
        worst_html = "".join([self._generate_example_case(r, "Worst") for r in worst_cases])
        critical_html = "".join([self._generate_example_case(r, "Critical") for r in critical_cases])

        return f"""
        <section class="examples">
            <h2>💡 Example Cases</h2>

            <h3 style="margin-top: 30px; color: #10b981;">✓ Best Performing Cases</h3>
            {best_html if best_html else "<p>No cases to display</p>"}

            <h3 style="margin-top: 30px; color: #ef4444;">⚠️ Worst Performing Cases</h3>
            {worst_html if worst_html else "<p>No cases to display</p>"}

            {f'<h3 style="margin-top: 30px; color: #dc2626;">🚨 Critical Failures</h3>{critical_html}' if critical_html else ''}
        </section>
        """

    def _generate_example_case(self, result: EvaluationResult, category: str) -> str:
        """Generate HTML for a single example case."""
        safety_badge = f'<span class="badge badge-{"safe" if not result.safety_flag else "unsafe"}">{"SAFE" if not result.safety_flag else "UNSAFE"}</span>'

        user_msgs = "<br>".join([f'<div class="user-message">User: {msg}</div>' for msg in result.user_messages])

        score_class = self._get_score_class(result.scores.overall_score)

        return f"""
        <div class="example-case">
            <div class="example-header">
                <div class="example-title">{result.test_id}</div>
                <div>{safety_badge}</div>
            </div>

            <div class="info-box">
                <strong>Domain:</strong> {result.domain} |
                <strong>Pattern:</strong> {result.harm_pattern} |
                <strong>Vulnerability:</strong> {result.vulnerability_level}
            </div>

            <div class="conversation-block">
                {user_msgs}
                <div class="ai-response"><strong>AI Response:</strong><br>{result.ai_response[:500]}{"..." if len(result.ai_response) > 500 else ""}</div>
            </div>

            <div class="scores-row">
                <div class="score-item">
                    <div class="score-item-label">Overall</div>
                    <div class="score-item-value {score_class}">{result.scores.overall_score:.2f}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">Safety & Dignity</div>
                    <div class="score-item-value">{result.scores.safety_dignity}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">Wellbeing</div>
                    <div class="score-item-value">{result.scores.longterm_wellbeing}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">Transparency</div>
                    <div class="score-item-value">{result.scores.transparency}</div>
                </div>
            </div>

            <div style="margin-top: 15px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                <strong>Evaluator Reasoning:</strong><br>
                {result.evaluator_reasoning}
            </div>
        </div>
        """

    def _generate_chart_js(self, results: BenchmarkResults) -> str:
        """Generate JavaScript for charts."""
        # Prepare data for charts
        domain_labels = list(results.results_by_domain.keys())
        domain_scores = [results.results_by_domain[k]['avg_score'] for k in domain_labels]

        pattern_labels = list(results.results_by_pattern.keys())
        pattern_scores = [results.results_by_pattern[k]['avg_score'] for k in pattern_labels]

        vuln_labels = list(results.results_by_vulnerability.keys())
        vuln_scores = [results.results_by_vulnerability[k]['avg_score'] for k in vuln_labels]

        return f"""
        // Domain Chart
        new Chart(document.getElementById('domainChart'), {{
            type: 'bar',
            data: {{
                labels: {domain_labels},
                datasets: [{{
                    label: 'Average Score',
                    data: {domain_scores},
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, max: 5 }}
                }}
            }}
        }});

        // Pattern Chart
        new Chart(document.getElementById('patternChart'), {{
            type: 'bar',
            data: {{
                labels: {pattern_labels},
                datasets: [{{
                    label: 'Average Score',
                    data: {pattern_scores},
                    backgroundColor: 'rgba(118, 75, 162, 0.6)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, max: 5 }}
                }}
            }}
        }});

        // Vulnerability Chart
        new Chart(document.getElementById('vulnerabilityChart'), {{
            type: 'bar',
            data: {{
                labels: {vuln_labels},
                datasets: [{{
                    label: 'Average Score',
                    data: {vuln_scores},
                    backgroundColor: 'rgba(245, 158, 11, 0.6)',
                    borderColor: 'rgba(245, 158, 11, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, max: 5 }}
                }}
            }}
        }});

        // Dimensions Chart
        new Chart(document.getElementById('dimensionsChart'), {{
            type: 'radar',
            data: {{
                labels: ['Safety & Dignity', 'Long-term Wellbeing', 'Transparency'],
                datasets: [{{
                    label: '{results.ai_system}',
                    data: [{results.safety_dignity_avg:.2f}, {results.longterm_wellbeing_avg:.2f}, {results.transparency_avg:.2f}],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{ beginAtZero: true, max: 5 }}
                }}
            }}
        }});
        """

    def _generate_footer(self) -> str:
        """Generate report footer."""
        return """
        <footer>
            <p>Generated by AWAB (AI Well-Being Alignment Benchmark)</p>
            <p>Part of the HumaneBench Project</p>
        </footer>
        """

    def _get_score_class(self, score: float) -> str:
        """Get CSS class based on score."""
        if score >= 4.0:
            return "score-excellent"
        elif score >= 3.0:
            return "score-good"
        elif score >= 2.0:
            return "score-fair"
        else:
            return "score-poor"
