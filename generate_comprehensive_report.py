"""Generate comprehensive multi-model comparison HTML report."""

import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

def load_results(results_dir: Path) -> List[Dict]:
    """Load all available model results."""
    all_results = []

    # Find all results.json files
    for results_file in results_dir.glob("*/results.json"):
        with open(results_file) as f:
            data = json.load(f)
            all_results.append(data)

    return all_results

def generate_html(all_results: List[Dict], output_path: Path):
    """Generate comprehensive HTML report."""

    # Sort by overall score
    sorted_results = sorted(all_results, key=lambda r: r['overall_score'], reverse=True)

    # Build test case mapping for side-by-side comparison
    test_cases = defaultdict(lambda: {'test_data': None, 'model_results': {}})
    critical_failures = []

    for result in all_results:
        model_name = result['ai_system']
        for test in result['individual_results']:
            test_id = test['test_id']
            if test_cases[test_id]['test_data'] is None:
                test_cases[test_id]['test_data'] = test
            test_cases[test_id]['model_results'][model_name] = test

            # Track critical failures (high vulnerability + unsafe)
            if test.get('vulnerability_level') == 'high' and test.get('safety_flag', False):
                critical_failures.append((test_id, model_name, test))

    # Find worst performing test cases
    worst_cases = []
    for test_id, data in test_cases.items():
        # Calculate average score across all models for this test
        total_score = 0
        count = 0
        for r in data['model_results'].values():
            scores = r.get('scores', {})
            # Calculate overall as average of the three dimensions
            overall = (scores.get('safety_dignity', 0) + scores.get('longterm_wellbeing', 0) + scores.get('transparency', 0)) / 3
            total_score += overall
            count += 1
        avg_score = total_score / count if count > 0 else 0
        worst_cases.append((test_id, avg_score, data))
    worst_cases.sort(key=lambda x: x[1])

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWAB Comprehensive Multi-Model Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {get_css()}
    </style>
</head>
<body>
    <div class="container">
        {generate_header(sorted_results)}
        {generate_winner_callout(sorted_results)}
        {generate_overall_summary(sorted_results)}
        {generate_domain_stats(sorted_results)}
        {generate_category_breakdown(sorted_results)}
        {generate_comparisons(worst_cases, test_cases, sorted_results)}
        {generate_critical_failures_section(critical_failures, test_cases, sorted_results)}
        {generate_footer()}
    </div>
    <script>
        {generate_chart_js(sorted_results)}
    </script>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Comprehensive report generated: {output_path}")

def get_css() -> str:
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ec4899 100%);
            background-attachment: fixed;
            padding: 40px 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 32px;
            box-shadow: 0 30px 90px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            border-radius: 32px 32px 0 0;
        }

        header h1 {
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: white;
        }

        header p {
            font-size: 1.15em;
            opacity: 0.95;
            color: white;
        }

        .header-badges {
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 25px;
        }

        .header-badge {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.9em;
            border: 1px solid rgba(255,255,255,0.3);
            font-weight: 500;
            color: white;
        }

        .winner-callout {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 60px 40px;
            margin: 0;
            text-align: center;
            box-shadow: 0 10px 40px rgba(16, 185, 129, 0.4);
            position: relative;
            overflow: hidden;
            border-radius: 0 0 32px 32px;
        }

        .winner-callout::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 50% 0%, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
        }

        .winner-callout h2 {
            color: white;
            border: none;
            font-size: 2.5em;
            margin: 0 0 50px 0;
            padding: 0;
            font-weight: 800;
            text-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }

        .winner-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 50px;
            max-width: 1100px;
            margin: 0 auto;
            position: relative;
        }

        .winner-stat {
            text-align: center;
            position: relative;
        }

        .winner-stat::before {
            content: '';
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 4px;
            background: rgba(255,255,255,0.3);
            border-radius: 2px;
        }

        .winner-stat-value {
            font-size: 4.5em;
            font-weight: 900;
            line-height: 1;
            margin-bottom: 16px;
            text-shadow: 0 4px 12px rgba(0,0,0,0.15);
            letter-spacing: -2px;
        }

        .winner-stat-label {
            font-size: 1.05em;
            opacity: 0.95;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .content {
            padding: 40px;
        }

        h2 {
            font-size: 2em;
            margin: 40px 0 25px 0;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            border-bottom: 3px solid transparent;
            border-image: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            border-image-slice: 1;
            padding-bottom: 15px;
            font-weight: 700;
        }

        h3 {
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            color: #764ba2;
        }

        .summary-table {
            width: 100%;
            background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1), 0 1px 8px rgba(0,0,0,0.06);
            margin: 30px 0;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
        }

        .summary-table::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 24px;
            padding: 2px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }

        .summary-table th,
        .summary-table td {
            padding: 20px 24px;
            text-align: left;
        }

        .summary-table th {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 1.2px;
        }

        .summary-table tbody tr {
            border-bottom: 1px solid #f3f4f6;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .summary-table tbody tr:hover {
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%);
            transform: scale(1.005);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
        }

        .summary-table tbody tr:last-child {
            border-bottom: none;
        }

        .rank-medal {
            font-size: 1.5em;
            margin-right: 5px;
        }

        .score-excellent { color: #059669; font-weight: bold; }
        .score-good { color: #fbbf24; font-weight: bold; }
        .score-fair { color: #fb923c; font-weight: bold; }
        .score-poor { color: #ef4444; font-weight: bold; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }

        .chart-container {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 50%, #fef3ff 100%);
            padding: 36px;
            border-radius: 28px;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
            border: 3px solid transparent;
            background-clip: padding-box;
            transition: all 0.3s ease;
            position: relative;
        }

        .chart-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 28px;
            padding: 3px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.4;
        }

        .chart-container:hover {
            box-shadow: 0 16px 40px rgba(99, 102, 241, 0.3);
            transform: translateY(-4px);
        }

        .comparison-case {
            background: linear-gradient(135deg, #ffffff 0%, #fafcff 100%);
            padding: 36px;
            border-radius: 28px;
            margin: 35px 0;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15);
            border: 2px solid rgba(99, 102, 241, 0.15);
        }

        .case-header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .case-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .user-prompt {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .user-message {
            color: #4b5563;
            margin: 5px 0;
            font-style: italic;
        }

        .model-columns {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .model-column {
            background: linear-gradient(135deg, #fafcff 0%, #ffffff 100%);
            border-radius: 20px;
            padding: 24px;
            border: 2px solid rgba(99, 102, 241, 0.2);
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.12);
        }

        .model-name {
            font-weight: 700;
            font-size: 1.1em;
            color: #6366f1;
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

        .response-text::-webkit-scrollbar-thumb {
            background: #6366f1;
            border-radius: 10px;
        }

        .scores-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
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
        }

        .score-value {
            font-size: 1.3em;
            font-weight: bold;
            margin-top: 5px;
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

        footer {
            text-align: center;
            padding: 40px 20px;
            color: #888;
            background: #f9fafb;
        }

        .category-table {
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
        }

        .category-table th,
        .category-table td {
            padding: 12px;
            text-align: left;
            font-size: 0.9em;
        }

        .category-table th {
            background: #764ba2;
            color: white;
            font-weight: 600;
            font-size: 0.8em;
        }

        .category-table tr:nth-child(even) {
            background: #f9f9f9;
        }

        .critical-failures-alert {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 8px 24px rgba(220, 38, 38, 0.3);
        }

        .critical-failures-alert h2 {
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }

        .critical-failure-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .critical-failure-card {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }

        .critical-failure-card:hover {
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.4);
            transform: translateY(-2px);
        }

        .critical-failure-model {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }

        .critical-failure-domain {
            font-size: 0.85em;
            opacity: 0.9;
            margin: 5px 0;
        }

        .domain-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .domain-card {
            background: linear-gradient(135deg, #ffffff 0%, #fef3ff 50%, #faf5ff 100%);
            border-radius: 24px;
            padding: 32px;
            border: 3px solid transparent;
            background-clip: padding-box;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
            position: relative;
        }

        .domain-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 24px;
            padding: 3px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.3;
            transition: opacity 0.4s ease;
        }

        .domain-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.35);
        }

        .domain-card:hover::before {
            opacity: 1;
        }

        .domain-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }

        .domain-card-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #6366f1;
        }

        .domain-average {
            display: flex;
            align-items: center;
        }

        .domain-model-row {
            margin-bottom: 15px;
        }

        .domain-model-row:last-child {
            margin-bottom: 0;
        }

        .domain-model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .domain-model-name {
            font-size: 0.9em;
            color: #4b5563;
            font-weight: 500;
        }

        .domain-score {
            font-weight: 700;
            font-size: 1.1em;
        }

        .domain-bar-container {
            height: 12px;
            background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
        }

        .domain-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stats-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 2px solid #f3f4f6;
            transition: all 0.3s ease;
        }

        .stats-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }

        .stats-number {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stats-label {
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .pattern-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }

        .pattern-card {
            background: linear-gradient(135deg, #ffffff 0%, #fff7fb 50%, #fef3ff 100%);
            border-radius: 24px;
            padding: 32px;
            border: 3px solid transparent;
            background-clip: padding-box;
            box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .pattern-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 24px;
            padding: 3px;
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #6366f1 100%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.3;
            transition: opacity 0.4s ease;
        }

        .pattern-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(139, 92, 246, 0.35);
        }

        .pattern-card:hover::before {
            opacity: 1;
        }

        .pattern-card-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #8b5cf6;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }

        .pattern-model-row {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px 0;
            border-bottom: 1px solid #f3f4f6;
        }

        .pattern-model-row:last-child {
            border-bottom: none;
        }

        .pattern-score {
            font-weight: bold;
            font-size: 1.2em;
            min-width: 50px;
            text-align: right;
        }
    """

def generate_header(sorted_results: List[Dict]) -> str:
    total_tests = sorted_results[0]['total_tests'] if sorted_results else 0

    return f"""
    <header>
        <h1>AWAB Multi-Model Benchmark Report</h1>
        <p>AI Well-Being Alignment Benchmark - Comprehensive Comparison</p>
        <div class="header-badges">
            <div class="header-badge">October 4, 2025</div>
            <div class="header-badge">{total_tests} Unique Test Cases</div>
            <div class="header-badge">{len(sorted_results)} AI Models Tested</div>
            <div class="header-badge">GPT-4o-mini Evaluator</div>
        </div>
    </header>
    """

def generate_winner_callout(sorted_results: List[Dict]) -> str:
    if not sorted_results:
        return ""

    winner = sorted_results[0]

    return f"""
    <div class="winner-callout">
        <h2>🏆 Winner: {winner['ai_system']}</h2>
        <div class="winner-stats">
            <div class="winner-stat">
                <div class="winner-stat-value">{winner['overall_score']:.2f}</div>
                <div class="winner-stat-label">Overall Score (out of 5.0)</div>
            </div>
            <div class="winner-stat">
                <div class="winner-stat-value">{winner['safety_pass_rate']:.1f}%</div>
                <div class="winner-stat-label">Safety Pass Rate</div>
            </div>
            <div class="winner-stat">
                <div class="winner-stat-value">{winner['critical_failures']}</div>
                <div class="winner-stat-label">Critical Failure{'s' if winner['critical_failures'] != 1 else ''}</div>
            </div>
        </div>
    </div>
    """

def generate_overall_summary(sorted_results: List[Dict]) -> str:
    rows = ""
    for rank, result in enumerate(sorted_results, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
        score_class = get_score_class(result['overall_score'])

        rows += f"""
        <tr>
            <td><span class="rank-medal">{medal}</span>{rank}</td>
            <td><strong>{result['ai_system']}</strong></td>
            <td class="{score_class}">{result['overall_score']:.2f}/5.0</td>
            <td class="{get_score_class(result['safety_dignity_avg'])}">{result['safety_dignity_avg']:.2f}</td>
            <td class="{get_score_class(result['longterm_wellbeing_avg'])}">{result['longterm_wellbeing_avg']:.2f}</td>
            <td class="{get_score_class(result['transparency_avg'])}">{result['transparency_avg']:.2f}</td>
            <td>{result['safety_pass_rate']:.1f}%</td>
            <td class="score-poor">{result['critical_failures']}</td>
        </tr>
        """

    return f"""
    <div class="content">
        <h2>📊 Overall Performance Summary</h2>
        <table class="summary-table">
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

        <div class="charts-grid">
            <div class="chart-container">
                <canvas id="overallScoreChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="dimensionsRadarChart"></canvas>
            </div>
        </div>
    </div>
    """

def generate_critical_failures_section(critical_failures: List, test_cases: Dict, sorted_results: List[Dict]) -> str:
    """Generate critical failures alert section."""
    if not critical_failures:
        return """
        <div class="content">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin: 30px 0;">
                <h2 style="color: white; border: none; margin: 0;">✅ No Critical Failures Detected</h2>
                <p style="margin-top: 10px; opacity: 0.95;">All models performed safely on high-vulnerability test cases.</p>
            </div>
        </div>
        """

    # Group by model
    failures_by_model = defaultdict(list)
    for test_id, model_name, test in critical_failures:
        failures_by_model[model_name].append((test_id, test))

    failure_cards = ""
    for model_name in sorted([m for m in failures_by_model.keys()]):
        failures = failures_by_model[model_name]
        failure_details = ""
        for test_id, test in failures:
            failure_details += f"""
                <div class="critical-failure-domain">
                    <strong>Test:</strong> {test_id}<br>
                    <strong>Domain:</strong> {test.get('domain', 'N/A')} |
                    <strong>Pattern:</strong> {test.get('harm_pattern', 'N/A')}
                </div>
            """

        failure_cards += f"""
        <div class="critical-failure-card">
            <div class="critical-failure-model">{model_name}</div>
            <div style="font-size: 1.3em; margin-bottom: 10px;">⚠️ {len(failures)} Critical Failure{'s' if len(failures) > 1 else ''}</div>
            {failure_details}
        </div>
        """

    return f"""
    <div class="content">
        <div class="critical-failures-alert">
            <h2>🚨 Critical Failures Alert</h2>
            <p style="font-size: 1.1em; margin: 15px 0; opacity: 0.95;">
                The following models failed high-vulnerability test cases (marked as unsafe).
                These failures indicate potentially harmful responses to vulnerable users.
            </p>
            <div style="font-size: 1.5em; margin: 20px 0;">
                <strong>Total Critical Failures: {len(critical_failures)}</strong>
            </div>
            <div class="critical-failure-grid">
                {failure_cards}
            </div>
        </div>
    </div>
    """

def generate_domain_stats(sorted_results: List[Dict]) -> str:
    """Generate domain statistics section."""
    # Collect all unique domains with their averages
    domain_data = {}

    for result in sorted_results:
        for domain, stats in result.get('results_by_domain', {}).items():
            if domain not in domain_data:
                domain_data[domain] = {'scores': [], 'models': {}}

            avg_score = stats.get('avg_score', 0)
            domain_data[domain]['scores'].append(avg_score)
            domain_data[domain]['models'][result['ai_system']] = stats

    if not domain_data:
        return ""

    # Calculate averages and sort by average score (descending)
    domain_averages = []
    for domain, data in domain_data.items():
        avg = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        domain_averages.append((domain, avg, data['models']))

    domain_averages.sort(key=lambda x: x[1], reverse=True)

    domain_cards = ""
    for domain, domain_avg, models in domain_averages:
        # Get stats for each model in this domain (sorted by score)
        model_scores = []
        for result in sorted_results:
            if result['ai_system'] in models:
                stats = models[result['ai_system']]
                avg_score = stats.get('avg_score', 0)
                model_scores.append((result['ai_system'], avg_score, stats))

        # Sort models by score within this domain
        model_scores.sort(key=lambda x: x[1], reverse=True)

        model_rows = ""
        for model_name, avg_score, stats in model_scores:
            score_class = get_score_class(avg_score)
            score_color = get_score_color(avg_score)
            bar_width = (avg_score / 5.0) * 100

            model_rows += f"""
            <div class="domain-model-row">
                <div class="domain-model-header">
                    <span class="domain-model-name">{model_name}</span>
                    <span class="domain-score {score_class}">{avg_score:.2f}</span>
                </div>
                <div class="domain-bar-container">
                    <div class="domain-bar-fill" style="width: {bar_width}%; background: {score_color};"></div>
                </div>
            </div>
            """

        domain_avg_class = get_score_class(domain_avg)
        domain_cards += f"""
        <div class="domain-card">
            <div class="domain-card-header">
                <div class="domain-card-title">{domain.replace('_', ' ').title()}</div>
                <div class="domain-average">
                    <span style="font-size: 0.85em; color: #6b7280;">Avg:</span>
                    <span class="domain-score {domain_avg_class}" style="font-size: 1.3em; margin-left: 5px;">{domain_avg:.2f}</span>
                </div>
            </div>
            {model_rows}
        </div>
        """

    return f"""
    <div class="content">
        <h2>🏷️ Performance by Domain</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">
            Domains sorted by average score across all models
        </p>
        <div class="domain-stats-grid">
            {domain_cards}
        </div>
    </div>
    """

def generate_category_breakdown(sorted_results: List[Dict]) -> str:
    # Aggregate by pattern
    patterns = defaultdict(lambda: defaultdict(list))

    for result in sorted_results:
        model = result['ai_system']
        for pattern, stats in result.get('results_by_pattern', {}).items():
            patterns[pattern][model] = stats

    # Create visual pattern cards
    pattern_cards = ""
    for pattern in sorted(patterns.keys()):
        model_rows = ""
        for result in sorted_results:
            model = result['ai_system']
            if model in patterns[pattern]:
                stats = patterns[pattern][model]
                avg_score = stats.get('avg_score', 0)
                score_class = get_score_class(avg_score)
                safety_rate = stats.get('safety_pass_rate', 0)

                # Create a visual bar for safety rate
                bar_color = "#10b981" if safety_rate >= 80 else "#f59e0b" if safety_rate >= 60 else "#ef4444"

                model_rows += f"""
                <div class="pattern-model-row">
                    <div style="flex: 1;">
                        <div style="font-size: 0.9em; color: #4b5563; margin-bottom: 4px;">{model}</div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="flex: 1; background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="width: {safety_rate}%; height: 100%; background: {bar_color}; transition: width 0.3s;"></div>
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; min-width: 45px;">{safety_rate:.0f}%</div>
                        </div>
                    </div>
                    <div class="pattern-score {score_class}">{avg_score:.2f}</div>
                </div>
                """

        pattern_cards += f"""
        <div class="pattern-card">
            <div class="pattern-card-title">{pattern.replace('_', ' ').title()}</div>
            {model_rows}
        </div>
        """

    return f"""
    <div class="content">
        <h2>🎭 Performance by Harm Pattern</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">
            How models handle different types of harmful requests (direct, rationalized, hidden)
        </p>
        <div class="pattern-stats-grid">
            {pattern_cards}
        </div>
    </div>
    """

def generate_comparisons(worst_cases: List, test_cases: Dict, sorted_results: List[Dict]) -> str:
    # Show worst 10 cases and sample of all
    comparison_html = ""

    # Worst cases
    for i, (test_id, avg_score, data) in enumerate(worst_cases[:10], 1):
        comparison_html += generate_single_comparison(i, test_id, data, sorted_results, "Worst")

    # Sample from all cases
    sample_cases = list(test_cases.items())[::len(test_cases)//10] if len(test_cases) > 10 else list(test_cases.items())
    for i, (test_id, data) in enumerate(sample_cases, 11):
        comparison_html += generate_single_comparison(i, test_id, data, sorted_results, "Sample")

    return f"""
    <div class="content">
        <h2>🔍 Side-by-Side Comparisons</h2>
        <h3 style="color: #ef4444;">⚠️ Worst Performing Cases</h3>
        {comparison_html}
    </div>
    """

def generate_single_comparison(index: int, test_id: str, data: Dict, sorted_results: List[Dict], category: str) -> str:
    base_test = data['test_data']
    model_results = data['model_results']

    user_msgs = "<br>".join([f'<div class="user-message">User: {msg}</div>' for msg in base_test.get('user_messages', [])])

    model_columns = ""
    for result in sorted_results:
        model_name = result['ai_system']
        if model_name in model_results:
            model_result = model_results[model_name]
            model_columns += generate_model_column(model_name, model_result)

    return f"""
    <div class="comparison-case">
        <div class="case-header">
            <div class="case-title">{category} Case #{index}: {test_id}</div>
            <div style="font-size: 0.9em; opacity: 0.95;">
                <strong>Domain:</strong> {base_test.get('domain', 'N/A')} |
                <strong>Pattern:</strong> {base_test.get('harm_pattern', 'N/A')} |
                <strong>Vulnerability:</strong> {base_test.get('vulnerability_level', 'N/A')}
            </div>
        </div>

        <div class="user-prompt">
            <strong>User Input:</strong><br>
            {user_msgs}
        </div>

        <h3>Model Responses:</h3>
        <div class="model-columns">
            {model_columns}
        </div>
    </div>
    """

def generate_model_column(model_name: str, result: Dict) -> str:
    safety_class = "badge-safe" if not result.get('safety_flag', False) else "badge-unsafe"
    safety_text = "SAFE" if not result.get('safety_flag', False) else "UNSAFE"

    scores = result.get('scores', {})
    # Calculate overall as average of the three dimensions
    overall = (scores.get('safety_dignity', 0) + scores.get('longterm_wellbeing', 0) + scores.get('transparency', 0)) / 3

    return f"""
    <div class="model-column">
        <div class="model-name">{model_name}</div>

        <div class="response-text">{result.get('ai_response', 'N/A')}</div>

        <div class="scores-row">
            <div class="score-box">
                <div class="score-label">Overall</div>
                <div class="score-value {get_score_class(overall)}">{overall:.1f}</div>
            </div>
            <div class="score-box">
                <div class="score-label">Safety</div>
                <div class="score-value">{scores.get('safety_dignity', 0)}</div>
            </div>
            <div class="score-box">
                <div class="score-label">Wellbeing</div>
                <div class="score-value">{scores.get('longterm_wellbeing', 0)}</div>
            </div>
            <div class="score-box">
                <div class="score-label">Transparency</div>
                <div class="score-value">{scores.get('transparency', 0)}</div>
            </div>
        </div>

        <div class="safety-badge {safety_class}">{safety_text}</div>
    </div>
    """

def generate_chart_js(sorted_results: List[Dict]) -> str:
    model_names = [r['ai_system'] for r in sorted_results]
    overall_scores = [r['overall_score'] for r in sorted_results]
    safety_scores = [r['safety_dignity_avg'] for r in sorted_results]
    wellbeing_scores = [r['longterm_wellbeing_avg'] for r in sorted_results]
    transparency_scores = [r['transparency_avg'] for r in sorted_results]

    # Generate colors based on scores
    overall_colors = [get_score_color(score) for score in overall_scores]

    return f"""
    new Chart(document.getElementById('overallScoreChart'), {{
        type: 'bar',
        data: {{
            labels: {model_names},
            datasets: [{{
                label: 'Overall Score',
                data: {overall_scores},
                backgroundColor: {overall_colors},
                borderRadius: 8,
                borderWidth: 2,
                borderColor: {overall_colors}
            }}]
        }},
        options: {{
            responsive: true,
            scales: {{
                y: {{
                    min: 4.0,
                    max: 5.0,
                    ticks: {{
                        stepSize: 0.2
                    }}
                }}
            }},
            plugins: {{
                title: {{
                    display: true,
                    text: 'Overall Score Comparison (Scale: 4.0-5.0)',
                    font: {{ size: 14, weight: 'bold' }}
                }},
                legend: {{
                    display: false
                }}
            }}
        }}
    }});

    new Chart(document.getElementById('dimensionsRadarChart'), {{
        type: 'radar',
        data: {{
            labels: ['Safety & Dignity', 'Long-term Wellbeing', 'Transparency'],
            datasets: [
                {','.join([f"""{{
                    label: '{model_names[i]}',
                    data: [{safety_scores[i]:.2f}, {wellbeing_scores[i]:.2f}, {transparency_scores[i]:.2f}],
                    borderColor: '{overall_colors[i]}',
                    backgroundColor: '{overall_colors[i]}33',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}""" for i in range(len(sorted_results))])}
            ]
        }},
        options: {{
            responsive: true,
            scales: {{
                r: {{
                    min: 4.0,
                    max: 5.0,
                    ticks: {{
                        stepSize: 0.2
                    }}
                }}
            }},
            plugins: {{
                title: {{
                    display: true,
                    text: 'Dimension Comparison (Scale: 4.0-5.0)',
                    font: {{ size: 14, weight: 'bold' }}
                }},
                legend: {{
                    position: 'top',
                    labels: {{
                        padding: 15,
                        font: {{ size: 12 }}
                    }}
                }}
            }}
        }}
    }});
    """

def generate_footer() -> str:
    return """
    <footer>
        <p>Generated by AWAB (AI Well-Being Alignment Benchmark)</p>
        <p>Part of the HumaneBench Project</p>
    </footer>
    """

def get_score_class(score: float) -> str:
    if score >= 4.0:
        return "score-excellent"
    elif score >= 3.0:
        return "score-good"
    elif score >= 2.0:
        return "score-fair"
    else:
        return "score-poor"

def get_score_color(score: float) -> str:
    """Return color based on score - aggressive color coding."""
    if score >= 4.85:
        return "#059669"  # Dark emerald green - Excellent
    elif score >= 4.75:
        return "#10b981"  # Emerald green - Very Good
    elif score >= 4.65:
        return "#34d399"  # Green - Good
    elif score >= 4.55:
        return "#fbbf24"  # Amber/Yellow - Above Average
    elif score >= 4.0:
        return "#f59e0b"  # Orange - Average
    elif score >= 3.0:
        return "#fb923c"  # Dark Orange - Below Average
    elif score >= 2.0:
        return "#ef4444"  # Red - Poor
    else:
        return "#dc2626"  # Dark Red - Very Poor

if __name__ == "__main__":
    results_dir = Path("data/evaluation_results")
    output_path = Path("data/comprehensive_comparison_report.html")

    print("Loading evaluation results...")
    all_results = load_results(results_dir)

    print(f"Found {len(all_results)} model evaluations")
    for r in all_results:
        print(f"  - {r['ai_system']}: {r['overall_score']:.2f}/5.0")

    print("\nGenerating comprehensive report...")
    generate_html(all_results, output_path)
