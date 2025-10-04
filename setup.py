"""Setup script for AWAB data generation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README_AWAB.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="awab-datagen",
    version="0.1.0",
    description="AI Well-Being Alignment Benchmark - Dataset Generation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HumaneBench",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "claude": ["anthropic>=0.21.0"],
        "openai": ["openai>=1.0.0"],
        "all": ["anthropic>=0.21.0", "openai>=1.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "awab-generate=awab_datagen.cli:cli",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
