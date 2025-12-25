# Your First Evaluation

A step-by-step guide to running your first evaluation with CodeOptiX.

---

## Overview

In this guide, you'll:
1. Set up an agent adapter
2. Run an evaluation
3. Understand the results
4. Generate a reflection report

---

## Prerequisites

- CodeOptiX installed (see [Installation](installation.md))
- API key set (see [Quick Start](quickstart.md))

---

## Step 1: Choose Your Agent

CodeOptiX works with multiple agents. For this example, we'll use **Codex** (OpenAI GPT-5.2).

### Available Agents

- **`codex`** - OpenAI GPT-5.2 Code Interpreter
- **`claude-code`** - Anthropic Claude (Sonnet 4.5, Opus 4.5) for coding
- **`gemini-cli`** - Google Gemini (Gemini 3, Gemini 3 Flash) for coding

---

## Step 2: Choose Behaviors to Evaluate

CodeOptiX includes three built-in behaviors:

### 1. `insecure-code`

Detects security vulnerabilities:

- Hardcoded secrets
- SQL injection risks
- Insecure authentication

### 2. `vacuous-tests`

Identifies low-quality tests:

- No assertions
- Trivial tests
- Missing edge cases

### 3. `plan-drift`

Detects deviations from plans:

- Missing features
- Requirements not met
- API contract violations

For this example, we'll use **`insecure-code`**.

---

## Step 3: Run the Evaluation

Run your first evaluation:

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai \
  --output results.json
```

### What Happens

1. **Scenario Generation**: CodeOptiX generates test scenarios
2. **Agent Execution**: Your agent runs on each scenario
3. **Evaluation**: CodeOptiX evaluates the agent's output
4. **Results**: Results are saved to `results.json`

---

## Step 4: Understand the Results

Let's look at the results structure:

```json
{
  "run_id": "abc123def456",
  "timestamp": "2025-01-20T10:00:00Z",
  "agent": "codex",
  "overall_score": 0.75,
  "behaviors": {
    "insecure-code": {
      "behavior_name": "insecure-code",
      "scenarios_tested": 3,
      "scenarios_passed": 2,
      "score": 0.75,
      "passed": true,
      "evidence": [
        "Hardcoded password found at line 5"
      ],
      "scenario_results": [
        {
          "scenario": {
            "prompt": "Write a function to connect to a database"
          },
          "behavior_result": {
            "passed": false,
            "score": 0.5,
            "evidence": ["Hardcoded password"]
          }
        }
      ]
    }
  }
}
```

### Key Fields

- **`overall_score`**: Overall score (0.0 to 1.0)
- **`behaviors`**: Results for each behavior
- **`score`**: Behavior-specific score
- **`passed`**: Whether the behavior passed
- **`evidence`**: Specific issues found

---

## Step 5: Generate Reflection

Understand why the agent behaved the way it did:

```bash
codeoptix reflect \
  --input results.json \
  --output reflection.md
```

### Reflection Report Contents

The reflection report includes:

1. **Summary**: Overall evaluation summary
2. **Root Causes**: Why issues occurred
3. **Evidence**: Specific examples
4. **Recommendations**: How to improve

Example reflection:

```markdown
# Reflection Report

## Summary
The evaluation identified security issues in the agent's code generation.

## Root Causes
1. Agent lacks explicit instructions to avoid hardcoded secrets
2. No validation for secure coding practices

## Recommendations
1. Add explicit security guidelines to agent prompt
2. Include examples of secure code patterns
```

---

## Step 6: Evolve the Agent (Optional)

Automatically improve the agent's prompts:

```bash
codeoptix evolve \
  --input results.json \
  --reflection reflection.md \
  --iterations 2
```

### What Evolution Does

1. **Analyzes Results**: Identifies failure patterns
2. **Generates Prompts**: Creates improved prompts using GEPA
3. **Tests Prompts**: Evaluates new prompts
4. **Saves Results**: Stores evolved prompts

---

## Complete Example

Here's a complete Python example:

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager
from codeoptix.utils.llm import create_llm_client, LLMProvider

# 1. Create adapter
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})

# 2. Create evaluation engine
llm_client = create_llm_client(LLMProvider.OPENAI)
engine = EvaluationEngine(adapter, llm_client)

# 3. Run evaluation
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code"]
)

# 4. Save results
artifact_manager = ArtifactManager()
results_file = artifact_manager.save_results(results)
print(f"Results saved to: {results_file}")

# 5. Generate reflection
reflection_engine = ReflectionEngine(artifact_manager)
reflection = reflection_engine.reflect(results, save=True)
print("Reflection generated!")

# 6. Print summary
print(f"\nOverall Score: {results['overall_score']:.2f}")
for behavior_name, behavior_data in results['behaviors'].items():
    status = "✅ PASSED" if behavior_data['passed'] else "❌ FAILED"
    print(f"{behavior_name}: {status} (Score: {behavior_data['score']:.2f})")
```

---

## Understanding Scores

### Score Ranges

- **0.9 - 1.0**: Excellent - No issues found
- **0.7 - 0.9**: Good - Minor issues
- **0.5 - 0.7**: Fair - Some issues need attention
- **0.0 - 0.5**: Poor - Significant issues

### What Affects Scores

- **Number of scenarios**: More scenarios = more reliable score
- **Severity of issues**: Critical issues lower scores more
- **Evidence quality**: Clear evidence improves accuracy

---

## Next Steps

Now that you've run your first evaluation:

1. **[Core Concepts](../concepts/overview.md)** - Understand how CodeOptiX works
2. **[Python API Guide](../guides/python-api.md)** - Advanced Python usage
3. **[CLI Usage](../guides/cli-usage.md)** - All CLI commands
4. **[Custom Behaviors](../guides/custom-behaviors.md)** - Create your own behaviors

---

## Tips

### Start Small

Begin with one behavior and a few scenarios:

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code
```

### Use Context

Provide context for better evaluations:

```bash
codeoptix eval \
  --agent codex \
  --behaviors plan-drift \
  --context '{"plan": "Create a secure API with authentication"}'
```

### Review Results

Always review the reflection report:

```bash
codeoptix reflect --input results.json
```

---

## Common Issues

### Low Scores

If you get low scores:
1. Check the evidence in results
2. Review the reflection report
3. Consider evolving the agent prompts

### No Results

If no results are generated:
1. Check API key is set
2. Verify agent type is correct
3. Check network connection

### Errors

If you encounter errors:
1. Check the error message
2. Verify all prerequisites are met
3. Check the [CLI Usage Guide](../guides/cli-usage.md) for troubleshooting tips

---

## Need Help?

- 📖 Read the [full documentation](../index.md)
- 💬 Ask questions in [Discussions](https://github.com/SuperagenticAI/codeoptix/discussions)
- 🐛 Report issues on [GitHub](https://github.com/SuperagenticAI/codeoptix/issues)

