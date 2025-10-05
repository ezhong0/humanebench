"""Report generation for benchmark results."""

from .html_report import HTMLReportGenerator
from .multi_model_comparison_html import MultiModelComparisonHTMLGenerator

__all__ = ["HTMLReportGenerator", "MultiModelComparisonHTMLGenerator"]
