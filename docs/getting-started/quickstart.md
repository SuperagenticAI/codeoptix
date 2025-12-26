# Quick Start

Get up and running with CodeOptiX in 5 minutes! This guide will walk you through your first evaluation.

---

## Step 1: Install CodeOptiX

If you haven't already, install CodeOptiX:

```bash
pip install codeoptix
```

---

## Step 2: Set Your API Key

!!! important "API Key Required for Full Features"
    **Without an API key**, CodeOptiX will only run basic static linters (ruff, bandit, flake8, etc.).
    
    **To unlock the full power** of CodeOptiX (behavioral evaluation, agent optimization, multi-LLM critique), **you must set an API key**.
    
    **We strongly recommend setting up an API key** to experience CodeOptiX's full capabilities.

Set your OpenAI API key (or use Anthropic/Google):

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

---

## Step 3: Run Your First Evaluation

Evaluate an agent for security issues:

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai
```

This command:

- ✅ Creates a Codex adapter
- ✅ Generates test scenarios
- ✅ Evaluates the agent's code
- ✅ Saves results to `.codeoptix/artifacts/results_*.json`

---

## Step 4: View Results

Check the results:

```bash
# List all runs
codeoptix list-runs

# View the latest results file
cat .codeoptix/artifacts/results_*.json | jq .
```

You'll see output like:

```json
{
  "run_id": "abc123",
  "overall_score": 0.75,
  "behaviors": {
    "insecure-code": {
      "score": 0.75,
      "passed": true,
      "evidence": []
    }
  }
}
```

---

## Step 5: Generate Reflection

Understand why the agent behaved the way it did:

```bash
codeoptix reflect --input .codeoptix/artifacts/results_*.json
```

This generates a reflection report explaining:
- What went well
- What needs improvement
- Root causes of issues
- Recommendations

---

## Step 6: Evolve the Agent (Optional)

Improve the agent's prompts automatically:

```bash
codeoptix evolve \
  --input .codeoptix/artifacts/results_*.json \
  --iterations 2
```

This will:
- Analyze the evaluation results
- Generate improved prompts
- Test the new prompts
- Save evolved prompts to `.codeoptix/artifacts/evolved_prompts_*.yaml`

---

## Complete Example

Here's a complete example using the Python API:

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

# 1. Create an adapter
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})

# 2. Create evaluation engine
llm_client = create_llm_client(LLMProvider.OPENAI)
engine = EvaluationEngine(adapter, llm_client)

# 3. Evaluate behaviors
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code", "vacuous-tests"]
)

# 4. Print results
print(f"Overall Score: {results['overall_score']:.2f}")
for behavior_name, behavior_data in results['behaviors'].items():
    print(f"{behavior_name}: {behavior_data['score']:.2f}")
```

---

## What's Next?

Now that you've run your first evaluation:

1. **[Your First Evaluation](first-evaluation.md)** - Detailed walkthrough
2. **[Core Concepts](../concepts/overview.md)** - Understand how CodeOptiX works
3. **[Python API Guide](../guides/python-api.md)** - Advanced usage
4. **[CLI Usage](../guides/cli-usage.md)** - All CLI commands

---

## Common Commands

Here are the most common commands you'll use:

```bash
# Evaluate agent
codeoptix eval --agent codex --behaviors insecure-code

# Generate reflection
codeoptix reflect --input results.json

# Evolve prompts
codeoptix evolve --input results.json

# Run full pipeline
codeoptix run --agent codex --behaviors insecure-code --evolve

# List all runs
codeoptix list-runs
```

---

## Tips for Beginners

### Start Simple

Begin with a single behavior:

```bash
codeoptix eval --agent codex --behaviors insecure-code
```

### Use Context

Provide context for better evaluations:

```bash
codeoptix eval \
  --agent codex \
  --behaviors plan-drift \
  --context '{"plan": "Create a secure API"}'
```

### Check Results

Always review the results:

```bash
codeoptix reflect --input results.json
```

---

## Troubleshooting

### "API key not found"

Make sure you've set your API key:

```bash
echo $OPENAI_API_KEY
```

### "Agent not found"

Check that you're using a supported agent:

- `codex` - OpenAI GPT-5.2
- `claude-code` - Anthropic Claude (Sonnet 4.5, Opus 4.5)
- `gemini-cli` - Google Gemini (Gemini 3, Gemini 3 Flash)

### "Behavior not found"

Use one of the built-in behaviors:

- `insecure-code` - Security vulnerabilities
- `vacuous-tests` - Test quality
- `plan-drift` - Plan alignment

---

## Need Help?

- 📖 Read the [full documentation](../index.md)
- 💬 Ask questions in [Discussions](https://github.com/SuperagenticAI/codeoptix/discussions)
- 🐛 Report issues on [GitHub](https://github.com/SuperagenticAI/codeoptix/issues)

