"""Multi-model comparison HTML report generator with side-by-side analysis."""

from pathlib import Path
from typing import List, Dict
from ..models import BenchmarkResults, EvaluationResult


class MultiModelComparisonHTMLGenerator:
    """Generates comprehensive HTML reports comparing multiple models."""

    def generate(self, all_results: List[BenchmarkResults], output_path: Path):
        """
        Generate multi-model comparison HTML report.

        Args:
            all_results: List of BenchmarkResults from different models
            output_path: Path to save HTML report
        """
        html = self._generate_html(all_results)

        with open(output_path, 'w') as f:
            f.write(html)

    def _generate_html(self, all_results: List[BenchmarkResults]) -> str:
        """Generate full HTML report."""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWAB Multi-Model Comparison Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(all_results)}
        {self._generate_overview(all_results)}
        {self._generate_comparison_charts(all_results)}
        {self._generate_side_by_side_comparisons(all_results)}
        {self._generate_footer()}
    </div>
    <script>
        {self._generate_chart_js(all_results)}
    </script>
</body>
</html>
"""
        return html

    def _get_css(self) -> str:
        """Get CSS styles for the report."""
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        header p {
            font-size: 1.1em;
            opacity: 0.95;
        }

        .content {
            padding: 40px;
        }

        h2 {
            font-size: 2em;
            margin: 40px 0 20px 0;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        h3 {
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            color: #764ba2;
        }

        .overview-table {
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
        }

        .overview-table th,
        .overview-table td {
            padding: 15px;
            text-align: left;
        }

        .overview-table th {
            background: #667eea;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }

        .overview-table tr:nth-child(even) {
            background: #f9f9f9;
        }

        .overview-table tr:hover {
            background: #f0f0f0;
        }

        .rank-medal {
            font-size: 1.5em;
            margin-right: 5px;
        }

        .score-excellent { color: #10b981; font-weight: bold; }
        .score-good { color: #3b82f6; font-weight: bold; }
        .score-fair { color: #f59e0b; font-weight: bold; }
        .score-poor { color: #ef4444; font-weight: bold; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }

        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }

        .test-case {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .test-case-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .test-case-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .test-case-meta {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9em;
            opacity: 0.95;
        }

        .user-prompt {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .user-prompt-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }

        .user-message {
            color: #4b5563;
            margin: 5px 0;
            font-style: italic;
        }

        .model-responses {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .model-response {
            background: #f9fafb;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e5e7eb;
            transition: all 0.3s ease;
        }

        .model-response:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }

        .model-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }

        .response-text {
            color: #1f2937;
            margin: 15px 0;
            line-height: 1.6;
            max-height: 300px;
            overflow-y: auto;
            padding-right: 10px;
        }

        .response-text::-webkit-scrollbar {
            width: 6px;
        }

        .response-text::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .response-text::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 10px;
        }

        .scores-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .score-box {
            background: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e5e7eb;
        }

        .score-label {
            font-size: 0.75em;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }

        .score-value {
            font-size: 1.3em;
            font-weight: bold;
        }

        .safety-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 10px;
        }

        .badge-safe {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-unsafe {
            background: #fee2e2;
            color: #991b1b;
        }

        .evaluator-reasoning {
            margin-top: 15px;
            padding: 15px;
            background: #fffbeb;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            font-size: 0.9em;
            color: #78350f;
        }

        .reasoning-label {
            font-weight: bold;
            margin-bottom: 5px;
        }

        footer {
            text-align: center;
            padding: 40px 20px;
            color: #888;
            margin-top: 50px;
            background: #f9fafb;
        }

        .nav-controls {
            position: sticky;
            top: 20px;
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
            z-index: 100;
        }

        .nav-controls button {
            padding: 10px 20px;
            margin: 5px;
            border: none;
            background: #667eea;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.3s;
        }

        .nav-controls button:hover {
            background: #764ba2;
        }

        .filter-controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px 0;
        }

        .filter-controls select {
            padding: 8px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 5px;
            font-size: 0.9em;
            cursor: pointer;
        }

        .filter-controls select:focus {
            outline: none;
            border-color: #667eea;
        }
        """

    def _generate_header(self, all_results: List[BenchmarkResults]) -> str:
        """Generate report header."""
        dataset_name = all_results[0].dataset_name if all_results else "Unknown"
        total_tests = all_results[0].total_tests if all_results else 0

        return f"""
        <header>
            <h1>🎯 AWAB Multi-Model Comparison Report</h1>
            <p style="font-size: 1.2em; opacity: 0.95; margin-top: 10px;">
                AI Well-Being Alignment Benchmark - Comprehensive Side-by-Side Analysis
            </p>
            <div style="margin-top: 20px; opacity: 0.9;">
                <p><strong>Models Evaluated:</strong> {len(all_results)}</p>
                <p><strong>Dataset:</strong> {dataset_name}</p>
                <p><strong>Total Test Cases:</strong> {total_tests}</p>
            </div>
        </header>
        """

    def _generate_overview(self, all_results: List[BenchmarkResults]) -> str:
        """Generate overview comparison table."""
        sorted_results = sorted(all_results, key=lambda r: r.overall_score, reverse=True)

        rows = ""
        for rank, result in enumerate(sorted_results, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            score_class = self._get_score_class(result.overall_score)

            rows += f"""
            <tr>
                <td><span class="rank-medal">{medal}</span>{rank}</td>
                <td><strong>{result.ai_system}</strong></td>
                <td class="{score_class}">{result.overall_score:.2f}/5.0</td>
                <td class="{self._get_score_class(result.safety_dignity_avg)}">{result.safety_dignity_avg:.2f}</td>
                <td class="{self._get_score_class(result.longterm_wellbeing_avg)}">{result.longterm_wellbeing_avg:.2f}</td>
                <td class="{self._get_score_class(result.transparency_avg)}">{result.transparency_avg:.2f}</td>
                <td>{result.safety_pass_rate:.1f}%</td>
                <td class="score-poor">{result.critical_failures}</td>
            </tr>
            """

        return f"""
        <div class="content">
            <h2>📊 Overall Performance Comparison</h2>
            <table class="overview-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Model</th>
                        <th>Overall Score</th>
                        <th>Safety & Dignity</th>
                        <th>Wellbeing</th>
                        <th>Transparency</th>
                        <th>Safety Pass Rate</th>
                        <th>Critical Failures</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """

    def _generate_comparison_charts(self, all_results: List[BenchmarkResults]) -> str:
        """Generate comparison charts section."""
        return """
        <div class="content">
            <h2>📈 Comparative Analysis</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Overall Score Comparison</div>
                    <canvas id="overallScoreChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Dimension Comparison (Radar)</div>
                    <canvas id="dimensionsRadarChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Safety Pass Rate</div>
                    <canvas id="safetyPassRateChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Critical Failures</div>
                    <canvas id="criticalFailuresChart"></canvas>
                </div>
            </div>
        </div>
        """

    def _generate_side_by_side_comparisons(self, all_results: List[BenchmarkResults]) -> str:
        """Generate side-by-side comparison of all test cases."""
        if not all_results:
            return ""

        # Create a mapping of test_id to results from all models
        test_cases = {}
        for result in all_results:
            for individual_result in result.individual_results:
                test_id = individual_result.test_id
                if test_id not in test_cases:
                    test_cases[test_id] = {
                        'test_data': individual_result,
                        'model_results': {}
                    }
                test_cases[test_id]['model_results'][result.ai_system] = individual_result

        # Generate HTML for each test case
        test_cases_html = ""
        for i, (test_id, test_data) in enumerate(test_cases.items(), 1):
            test_cases_html += self._generate_test_case_comparison(i, test_id, test_data, all_results)

        return f"""
        <div class="content">
            <h2>🔍 Side-by-Side Test Case Comparisons</h2>
            <div class="nav-controls">
                <div class="filter-controls">
                    <label>
                        Filter by Domain:
                        <select id="domainFilter" onchange="filterTestCases()">
                            <option value="all">All Domains</option>
                        </select>
                    </label>
                    <label>
                        Filter by Harm Pattern:
                        <select id="patternFilter" onchange="filterTestCases()">
                            <option value="all">All Patterns</option>
                        </select>
                    </label>
                    <label>
                        Filter by Vulnerability:
                        <select id="vulnFilter" onchange="filterTestCases()">
                            <option value="all">All Levels</option>
                        </select>
                    </label>
                </div>
                <div>
                    <button onclick="scrollToTop()">⬆ Top</button>
                    <button onclick="expandAll()">Expand All</button>
                    <button onclick="collapseAll()">Collapse All</button>
                </div>
            </div>
            <div id="testCasesContainer">
                {test_cases_html}
            </div>
        </div>
        <script>
            function scrollToTop() {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}

            function expandAll() {{
                document.querySelectorAll('.model-response .response-text').forEach(el => {{
                    el.style.maxHeight = 'none';
                }});
            }}

            function collapseAll() {{
                document.querySelectorAll('.model-response .response-text').forEach(el => {{
                    el.style.maxHeight = '300px';
                }});
            }}

            function filterTestCases() {{
                const domain = document.getElementById('domainFilter').value;
                const pattern = document.getElementById('patternFilter').value;
                const vuln = document.getElementById('vulnFilter').value;

                document.querySelectorAll('.test-case').forEach(testCase => {{
                    const testDomain = testCase.dataset.domain;
                    const testPattern = testCase.dataset.pattern;
                    const testVuln = testCase.dataset.vulnerability;

                    const domainMatch = domain === 'all' || testDomain === domain;
                    const patternMatch = pattern === 'all' || testPattern === pattern;
                    const vulnMatch = vuln === 'all' || testVuln === vuln;

                    if (domainMatch && patternMatch && vulnMatch) {{
                        testCase.style.display = 'block';
                    }} else {{
                        testCase.style.display = 'none';
                    }}
                }});
            }}
        </script>
        """

    def _generate_test_case_comparison(self, index: int, test_id: str, test_data: dict, all_results: List[BenchmarkResults]) -> str:
        """Generate HTML for a single test case showing all model responses side-by-side."""
        base_test = test_data['test_data']
        model_results = test_data['model_results']

        # Generate user messages
        user_msgs_html = "<br>".join([f'<div class="user-message">User: {msg}</div>' for msg in base_test.user_messages])

        # Generate model responses grid
        model_responses_html = ""
        for result in all_results:
            model_name = result.ai_system
            if model_name in model_results:
                model_result = model_results[model_name]
                model_responses_html += self._generate_model_response_card(model_name, model_result)

        return f"""
        <div class="test-case" data-domain="{base_test.domain}" data-pattern="{base_test.harm_pattern}" data-vulnerability="{base_test.vulnerability_level}">
            <div class="test-case-header">
                <div class="test-case-title">Test Case #{index}: {test_id}</div>
                <div class="test-case-meta">
                    <span><strong>Domain:</strong> {base_test.domain}</span>
                    <span><strong>Harm Pattern:</strong> {base_test.harm_pattern}</span>
                    <span><strong>Vulnerability:</strong> {base_test.vulnerability_level}</span>
                </div>
            </div>

            <div class="user-prompt">
                <div class="user-prompt-label">User Input:</div>
                {user_msgs_html}
            </div>

            <h3 style="margin: 25px 0 15px 0; color: #667eea;">Model Responses:</h3>
            <div class="model-responses">
                {model_responses_html}
            </div>
        </div>
        """

    def _generate_model_response_card(self, model_name: str, result: EvaluationResult) -> str:
        """Generate a card showing a single model's response and scores."""
        safety_badge_class = "badge-safe" if not result.safety_flag else "badge-unsafe"
        safety_badge_text = "SAFE" if not result.safety_flag else "UNSAFE"

        overall_score_class = self._get_score_class(result.scores.overall_score)

        return f"""
        <div class="model-response">
            <div class="model-name">{model_name}</div>

            <div class="response-text">{result.ai_response}</div>

            <div class="scores-grid">
                <div class="score-box">
                    <div class="score-label">Overall</div>
                    <div class="score-value {overall_score_class}">{result.scores.overall_score:.2f}</div>
                </div>
                <div class="score-box">
                    <div class="score-label">Safety</div>
                    <div class="score-value">{result.scores.safety_dignity}</div>
                </div>
                <div class="score-box">
                    <div class="score-label">Wellbeing</div>
                    <div class="score-value">{result.scores.longterm_wellbeing}</div>
                </div>
                <div class="score-box">
                    <div class="score-label">Transparency</div>
                    <div class="score-value">{result.scores.transparency}</div>
                </div>
            </div>

            <div class="safety-badge {safety_badge_class}">{safety_badge_text}</div>

            <div class="evaluator-reasoning">
                <div class="reasoning-label">Evaluator Reasoning:</div>
                {result.evaluator_reasoning}
            </div>
        </div>
        """

    def _generate_chart_js(self, all_results: List[BenchmarkResults]) -> str:
        """Generate JavaScript for charts."""
        model_names = [r.ai_system for r in all_results]
        overall_scores = [r.overall_score for r in all_results]
        safety_scores = [r.safety_dignity_avg for r in all_results]
        wellbeing_scores = [r.longterm_wellbeing_avg for r in all_results]
        transparency_scores = [r.transparency_avg for r in all_results]
        safety_pass_rates = [r.safety_pass_rate for r in all_results]
        critical_failures = [r.critical_failures for r in all_results]

        # Generate colors for each model
        colors = ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444'][:len(all_results)]

        return f"""
        // Overall Score Comparison
        new Chart(document.getElementById('overallScoreChart'), {{
            type: 'bar',
            data: {{
                labels: {model_names},
                datasets: [{{
                    label: 'Overall Score',
                    data: {overall_scores},
                    backgroundColor: {colors},
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

        // Dimensions Radar Chart
        new Chart(document.getElementById('dimensionsRadarChart'), {{
            type: 'radar',
            data: {{
                labels: ['Safety & Dignity', 'Long-term Wellbeing', 'Transparency'],
                datasets: [
                    {','.join([f"""{{
                        label: '{model_names[i]}',
                        data: [{safety_scores[i]:.2f}, {wellbeing_scores[i]:.2f}, {transparency_scores[i]:.2f}],
                        borderColor: '{colors[i]}',
                        backgroundColor: '{colors[i]}33',
                        borderWidth: 2
                    }}""" for i in range(len(all_results))])}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{ beginAtZero: true, max: 5 }}
                }}
            }}
        }});

        // Safety Pass Rate
        new Chart(document.getElementById('safetyPassRateChart'), {{
            type: 'bar',
            data: {{
                labels: {model_names},
                datasets: [{{
                    label: 'Safety Pass Rate (%)',
                    data: {safety_pass_rates},
                    backgroundColor: {colors},
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, max: 100 }}
                }}
            }}
        }});

        // Critical Failures
        new Chart(document.getElementById('criticalFailuresChart'), {{
            type: 'bar',
            data: {{
                labels: {model_names},
                datasets: [{{
                    label: 'Critical Failures',
                    data: {critical_failures},
                    backgroundColor: '#ef4444',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Populate filter dropdowns
        const domains = new Set();
        const patterns = new Set();
        const vulns = new Set();

        document.querySelectorAll('.test-case').forEach(testCase => {{
            domains.add(testCase.dataset.domain);
            patterns.add(testCase.dataset.pattern);
            vulns.add(testCase.dataset.vulnerability);
        }});

        const domainFilter = document.getElementById('domainFilter');
        domains.forEach(domain => {{
            const option = document.createElement('option');
            option.value = domain;
            option.textContent = domain;
            domainFilter.appendChild(option);
        }});

        const patternFilter = document.getElementById('patternFilter');
        patterns.forEach(pattern => {{
            const option = document.createElement('option');
            option.value = pattern;
            option.textContent = pattern;
            patternFilter.appendChild(option);
        }});

        const vulnFilter = document.getElementById('vulnFilter');
        vulns.forEach(vuln => {{
            const option = document.createElement('option');
            option.value = vuln;
            option.textContent = vuln;
            vulnFilter.appendChild(option);
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
