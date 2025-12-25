# Configuration Guide

Complete guide to configuring CodeOptiX.

---

## Configuration Methods

CodeOptiX can be configured via:
1. Configuration files (YAML/JSON)
2. Environment variables
3. Python code
4. Command-line arguments

---

## Configuration File Format

### YAML Configuration

Create `codeoptix.yaml`:

```yaml
adapter:
  llm_config:
    provider: openai
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}

evaluation:
  scenario_generator:
    num_scenarios: 3
    use_bloom: true
    use_full_bloom: true
  static_analysis:
    bandit: true
  test_runner:
    coverage: true

evolution:
  max_iterations: 3
  population_size: 3
  minibatch_size: 2
  proposer:
    use_gepa: true
    model: gpt-4o
```

### JSON Configuration

Create `codeoptix.json`:

```json
{
  "adapter": {
    "llm_config": {
      "provider": "openai",
      "model": "gpt-4o",
      "api_key": "${OPENAI_API_KEY}"
    }
  },
  "evaluation": {
    "scenario_generator": {
      "num_scenarios": 3,
      "use_bloom": true
    }
  }
}
```

---

## Adapter Configuration

### LLM Configuration

```yaml
adapter:
  llm_config:
    provider: openai  # or "anthropic", "google"
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}
  prompt: "You are a helpful coding assistant."
```

### Supported Providers

- `openai`: OpenAI GPT models
- `anthropic`: Anthropic Claude models
- `google`: Google Gemini models

---

## Evaluation Configuration

### Scenario Generator

```yaml
evaluation:
  scenario_generator:
    num_scenarios: 3        # Number of scenarios per behavior
    use_bloom: true         # Use Bloom-style generation
    use_full_bloom: true    # Full Bloom integration
    num_variations: 2       # Variations per scenario
    model: gpt-4o          # LLM model for generation
```

### Static Analysis

```yaml
evaluation:
  static_analysis:
    bandit: true  # Enable Bandit security checks
```

### Test Runner

```yaml
evaluation:
  test_runner:
    coverage: true  # Enable coverage analysis
```

### LLM Evaluator

```yaml
evaluation:
  llm_evaluator:
    model: gpt-4o
    temperature: 0.3
```

---

## Evolution Configuration

### Evolution Parameters

```yaml
evolution:
  max_iterations: 3           # Maximum iterations
  population_size: 3          # Candidates per iteration
  minibatch_size: 2           # Scenarios per evaluation
  improvement_threshold: 0.05 # Minimum improvement
```

### Proposer Configuration

```yaml
evolution:
  proposer:
    use_gepa: true      # Use GEPA for proposal
    model: gpt-4o       # LLM model
    temperature: 0.7    # Generation temperature
```

---

## Behavior Configuration

### Behavior-Specific Config

```yaml
behaviors:
  insecure-code:
    severity: high
    enabled: true
    strict_mode: true
  vacuous-tests:
    severity: medium
    enabled: true
```

---

## Environment Variables

### API Keys

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### Configuration Override

```bash
export CODEFLECT_CONFIG="path/to/config.yaml"
```

---

## Python Configuration

### Programmatic Configuration

```python
config = {
    "evaluation": {
        "scenario_generator": {
            "num_scenarios": 5
        }
    }
}

engine = EvaluationEngine(adapter, llm_client, config=config)
```

---

## Configuration Precedence

1. Command-line arguments (highest priority)
2. Configuration file
3. Environment variables
4. Default values (lowest priority)

---

## Best Practices

### 1. Use Configuration Files

Store configuration in files for reproducibility:

```yaml
# codeoptix.yaml
evaluation:
  scenario_generator:
    num_scenarios: 3
```

### 2. Use Environment Variables for Secrets

Never commit API keys:

```yaml
adapter:
  llm_config:
    api_key: ${OPENAI_API_KEY}  # Use env var
```

### 3. Version Control Configurations

Commit configuration files (without secrets):

```bash
git add codeoptix.yaml
git commit -m "Add CodeOptiX configuration"
```

---

## Next Steps

- [Python API Guide](python-api.md) - Use configuration in Python
- [CLI Usage Guide](cli-usage.md) - Command-line configuration
- [GitHub Actions Guide](github-actions.md) - CI/CD configuration

