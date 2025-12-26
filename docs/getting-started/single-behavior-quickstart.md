# Quick Start: Single Behavior

The easiest way to get started with CodeOptiX is to use a **single behavior**. This guide will help you run your first evaluation in under 5 minutes.

## Prerequisites

1. **Python 3.12+** installed
2. **API Key** for one of these providers:
   - OpenAI (for evaluation)
   - Anthropic (for Claude Code agent)
   - Google (for Gemini agent)

## Step 1: Install CodeOptiX

```bash
pip install codeoptix
```

Or using `uv` (recommended):

```bash
uv pip install codeoptix
```

## Step 2: Set Your API Key

```bash
export OPENAI_API_KEY="your-key-here"
```

Or for Claude Code:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Step 3: Run Your First Evaluation

### Option 1: Using the CLI (Easiest)

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors "insecure-code" \
  --llm-provider openai
```

This will:

- ✅ Check for security issues (insecure-code behavior)
- ✅ Use Claude Code as the agent
- ✅ Use OpenAI for evaluation
- ✅ Save results automatically

### Option 2: Using a Config File (Recommended)

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors "insecure-code" \
  --config examples/configs/single-behavior-insecure-code.yaml
```

### Option 3: Using Python

```python
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client
import os

# Create adapter
adapter = create_adapter("claude-code", {
    "llm_config": {
        "provider": "anthropic",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    }
})

# Create LLM client
llm_client = create_llm_client(LLMProvider.OPENAI, api_key=os.getenv("OPENAI_API_KEY"))

# Create evaluation engine
eval_engine = EvaluationEngine(adapter, llm_client)

# Run evaluation with single behavior
results = eval_engine.evaluate_behaviors(
    behavior_names=["insecure-code"]  # Behavior name as string
)

print(f"Score: {results['overall_score']:.2%}")
```

## Available Behaviors

You can use any of these behaviors:

### 1. insecure-code (Security)

**Behavior Name:** `insecure-code`

Checks for security vulnerabilities:
- Hardcoded secrets
- SQL injection risks
- XSS vulnerabilities

```bash
codeoptix eval --agent claude-code --behaviors "insecure-code"
```

**Behavior Name:** `insecure-code`

### 2. vacuous-tests (Test Quality)

**Behavior Name:** `vacuous-tests`

Checks test quality:
- Missing assertions
- Trivial tests
- Test coverage

```bash
codeoptix eval --agent claude-code --behaviors "vacuous-tests"
```

**Behavior Name:** `vacuous-tests`

### 3. plan-drift (Requirements)

**Behavior Name:** `plan-drift`

Checks requirements alignment:
- Plan deviations
- Missing features
- Extra features

```bash
codeoptix eval --agent claude-code --behaviors "plan-drift"
```

**Behavior Name:** `plan-drift`

## Understanding Results

After running an evaluation, you'll see:

```
✅ Evaluation Complete!
📊 Overall Score: 85.00%
📁 Results: artifacts/results_run-001.json
🆔 Run ID: run-001

📋 Behavior Results:

   ✅ **insecure-code**: 85.00%
```

### What the Score Means

- **100%**: Perfect - no issues found
- **80-99%**: Good - minor issues
- **50-79%**: Needs improvement
- **<50%**: Critical issues found

### Viewing Detailed Results

```bash
# View the results file
cat artifacts/results_run-001.json

# Generate a reflection report
codeoptix reflect --input artifacts/results_run-001.json
```

## Common Issues

### "API key required" Error

**Solution**: Set your API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

### "Unsupported adapter type" Error

**Solution**: Use a supported agent:
- `claude-code` (Anthropic)
- `codex` (OpenAI)
- `gemini-cli` (Google)

### "Invalid behavior name" Error

**Solution**: Use a valid behavior:

- **`insecure-code`**

- **`vacuous-tests`**

- **`plan-drift`**

## Next Steps

Once you're comfortable with a single behavior:

1. **Try other behaviors** - Test different aspects of code quality
2. **Use multiple behaviors** - Combine checks:
   ```bash
   codeoptix eval --agent claude-code --behaviors "insecure-code,vacuous-tests"
   ```
3. **Use in CI/CD** - Add to GitHub Actions:
   ```bash
   codeoptix ci --agent codex --behaviors "insecure-code" --fail-on-failure
   ```
4. **Generate reflection** - Understand failures:
   ```bash
   codeoptix reflect --input results.json
   ```

## Example Configurations

We provide example configs for single behaviors:

- `examples/configs/single-behavior-insecure-code.yaml` - Security checks
- `examples/configs/single-behavior-vacuous-tests.yaml` - Test quality
- `examples/configs/single-behavior-plan-drift.yaml` - Requirements alignment

## Getting Help

- 📖 [Full Documentation](../index.md)
- 💬 [GitHub Issues](https://github.com/SuperagenticAI/codeoptix/issues)
- 📧 [Support](mailto:codeoptix@super-agentic.ai)

