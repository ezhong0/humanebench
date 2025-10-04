# AWAB Quick Start Guide

## Installation

```bash
# Install dependencies (use virtual environment if needed)
pip install pydantic click pyyaml jinja2 python-dotenv

# Or install everything from requirements.txt
pip install -r requirements.txt
```

## Generate Dataset (Using Your OpenAI API Key)

Since you already have `.env` with `OPENAI_API_KEY`, you can run directly:

```bash
# Generate dataset with OpenAI (gpt-5-mini)
python3 -m awab_datagen.cli generate --provider openai

# Or with AI responses
python3 -m awab_datagen.cli generate --provider openai --generate-responses
```

## View Statistics

```bash
# See what templates are loaded
python3 -m awab_datagen.cli stats
```

## Output

Data will be generated in:
- `data/output/dataset.jsonl` - Main dataset
- `data/output/dataset_stats.json` - Statistics

## Example Usage

### 1. Generate with mock (no API calls - for testing)
```bash
python3 -m awab_datagen.cli generate --provider mock --personas 2
```

### 2. Generate with OpenAI (uses your .env file)
```bash
python3 -m awab_datagen.cli generate \
  --provider openai \
  --personas 3 \
  --generate-responses
```

### 3. Use custom model
```bash
python3 -m awab_datagen.cli generate \
  --provider openai \
  --model gpt-4o \
  --personas 5
```

### 4. Custom output directory
```bash
python3 -m awab_datagen.cli generate \
  --provider openai \
  --output data/my_custom_output \
  --personas 3
```

## What Gets Generated

Based on the current templates:

- **Mental Health**: 3 scenarios (direct, hidden, rationalized)
- **Medical**: 3 scenarios (misinformed, direct, hidden)
- **Financial**: 3 scenarios (rationalized, direct, misinformed)
- **Relationships**: 3 scenarios (hidden, rationalized, direct)

With `--personas 3` (default), you'll get:
- 12 scenarios × 3 personas = **36 total conversations**

## Programmatic Usage

```python
from pathlib import Path
from awab_datagen import PipelineConfig, DataGenerationPipeline
from awab_datagen.generation import OpenAIClient

# Create config
config = PipelineConfig(
    template_dir=Path("awab_datagen/templates/library"),
    output_dir=Path("data/output"),
    personas_per_scenario=3,
    llm_provider="openai",
    llm_api_key="your-key-or-use-env-var",
    llm_model="gpt-5-mini"
)

# Initialize with OpenAI client
llm_client = OpenAIClient(api_key=config.llm_api_key, model=config.llm_model)

# Run pipeline
pipeline = DataGenerationPipeline(config, llm_client)
datapoints = pipeline.run(generate_ai_responses=True)

print(f"Generated {len(datapoints)} conversations")

# Access individual datapoints
for dp in datapoints[:5]:
    print(f"{dp.id}: {dp.domain.value} - {dp.vulnerability_level.value}")
    print(f"  Persona: {dp.persona.to_description()}")
    print(f"  Turns: {len(dp.conversation)}")
```

## Next Steps

1. **Add More Templates**: Create YAML files in `awab_datagen/templates/library/`
2. **Customize Personas**: Modify `persona_hints` in templates
3. **Evaluate Responses**: Load `data/output/dataset.jsonl` for evaluation
4. **Scale Up**: Increase `--personas` for larger datasets

## Troubleshooting

### "No module named 'pydantic'"
```bash
pip install pydantic click pyyaml jinja2 python-dotenv
```

### "API key required"
Make sure `.env` file exists with:
```
OPENAI_API_KEY=sk-...
```

Or set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### "No templates found"
Run from the project root directory where `awab_datagen/` folder exists.
