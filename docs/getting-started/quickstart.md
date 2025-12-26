# Quick Start

Get up and running with CodeOptiX in 5 minutes! This guide will walk you through your first evaluation.

---

## Step 1: Install CodeOptiX

If you haven't already, install CodeOptiX:

```bash
pip install codeoptix
```

---

## Step 2: Choose Your Setup

### Option A: Ollama (Free, No API Key Required) 🆓

**Perfect for getting started!** Use local Ollama models - no API keys, no costs, works offline.

```bash
# Install Ollama (https://ollama.com)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.2:3b

# Run evaluation
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider ollama
```

### Option B: Cloud Providers (Requires API Key) ☁️

Use OpenAI, Anthropic, or Google models for more advanced evaluations.

Set your API key:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
# OR
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
# OR
export GOOGLE_API_KEY="your-api-key-here"
```

---

## Step 3: Run Your First Evaluation

!!! tip "Start with Ollama - It's Free & Works Offline!"
    **Recommended for first-time users!** Skip API keys and start evaluating immediately.

### Quick Test with Ollama (Recommended)

```bash
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider ollama
```

**Expected Output:**
```
🔍 CodeOptiX Evaluation
============================================================
📊 Agent: basic
📋 Behavior(s): insecure-code
✅ Adapter created: basic
🧠 Using local Ollama provider.

🚀 Running evaluation...
============================================================
✅ Evaluation Complete!
============================================================
📊 Overall Score: 85.71%
📁 Results: .codeoptix/artifacts/results_*.json
```

### Advanced Evaluation with Cloud Providers

For more advanced analysis using latest models:

```bash
# OpenAI GPT-5.2
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider openai

# Anthropic Claude Opus 4.5
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider anthropic
```

### What Happens During Evaluation

**All commands will:**

- **✅ Create the specified agent adapter**
  - Sets up the evaluation environment
- **✅ Generate test scenarios**
  - Creates diverse security test cases automatically
- **✅ Run behavioral analysis**
  - Evaluates the agent against each scenario
- **✅ Save detailed results**
  - Stores everything in `.codeoptix/artifacts/results_*.json`

---

## Step 4: Check Your Results

### View Evaluation Summary

CodeOptiX automatically saves results. Check them:

```bash
# List all evaluation runs
codeoptix list-runs

# View detailed results (requires jq for pretty printing)
cat .codeoptix/artifacts/results_*.json | jq .
```

### Understanding Your Results

**High Score (80-100%)**: Your agent performs well on security evaluation
**Medium Score (50-79%)**: Some security issues detected - review recommendations
**Low Score (0-49%)**: Significant security concerns - needs improvement

**Sample Results:**
```json
{
  "run_id": "7d42c92c",
  "overall_score": 0.857,  // 85.7% - Good performance!
  "behaviors": {
    "insecure-code": {
      "score": 0.857,
      "passed": true,        // ✅ Evaluation passed
      "evidence": []         // No critical issues found
    }
  }
}
```

**Key Metrics:**
- **`overall_score`**: 0.0 to 1.0 (higher is better)
- **`passed`**: `true` if behavior requirements met
- **`evidence`**: Specific issues or examples found

---

## Step 5: Generate Reflection Report

Get deep insights into your agent's performance:

```bash
codeoptix reflect --input .codeoptix/artifacts/results_*.json
```

**This generates a comprehensive reflection report explaining:**

- **✅ What went well**
  - Analysis of successful behaviors and patterns
- **🔍 What needs improvement**
  - Identification of problematic patterns
- **🔧 Root causes of issues**
  - Deep analysis of why problems occurred
- **💡 Actionable recommendations**
  - Specific suggestions for improvement

---

## Step 6: Evolve the Agent (Advanced)

Automatically improve your agent's prompts using AI:

```bash
codeoptix evolve \
  --input .codeoptix/artifacts/results_*.json \
  --iterations 2
```

**Evolution Process:**

- **🔍 Analyzes evaluation results**
  - Identifies patterns and issues
- **🧠 Generates improved prompts**
  - Uses GEPA optimization algorithm
- **🧪 Tests new prompts**
  - Validates improvements work
- **💾 Saves evolved prompts**
  - Stores in `.codeoptix/artifacts/evolved_prompts_*.yaml`

!!! note "Evolution requires API keys"
    This advanced feature needs cloud LLM access for the optimization process.

---

## Complete Python Example

Here's a complete example using Ollama (no API keys needed):

```python
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

# 1. Create a basic adapter with Ollama
adapter = create_adapter("basic", {
    "llm_config": {
        "provider": "ollama",
        "model": "llama3.2:3b"  # Use any installed Ollama model
    }
})

# 2. Create evaluation engine
llm_client = create_llm_client(LLMProvider.OLLAMA)
engine = EvaluationEngine(adapter, llm_client)

# 3. Evaluate behaviors
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code"]
)

# 4. Print results
print(f"Overall Score: {results['overall_score']:.1%}")
for behavior_name, behavior_data in results['behaviors'].items():
    status = "✅ PASS" if behavior_data['passed'] else "❌ FAIL"
    print(f"{behavior_name}: {behavior_data['score']:.1%} {status}")
```

**Expected Output:**
```
Overall Score: 85.7%
insecure-code: 85.7% ✅ PASS
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

