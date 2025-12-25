# CodeOptiX Examples

This directory contains example scripts demonstrating CodeOptiX's capabilities.

## Examples

### 1. Quick Start: Single Behavior (`quickstart-single-behavior.py`) ⭐

Perfect for getting started with CodeOptiX. Demonstrates evaluating code with a single behavior.

```bash
python examples/quickstart-single-behavior.py
```

**What it shows:**
- Setting up CodeOptiX with minimal configuration
- Running evaluation with a single behavior (insecure-code)
- Understanding evaluation results
- Using the CLI

### 2. Basic Adapter Usage (`basic_adapter_usage.py`)

Demonstrates how to create and use agent adapters with different LLM providers.

```bash
python examples/basic_adapter_usage.py
```

**What it shows:**
- Creating adapters for Claude Code, Codex, and Gemini CLI
- Executing tasks with different agents
- Handling agent outputs

### 3. Behavioral Spec Example (`behavioral_spec_example.py`) ⭐

**Complete end-to-end example** demonstrating a real-world behavioral spec scenario.

```bash
python examples/behavioral_spec_example.py
```

**What it shows:**
- Full pipeline: Evaluate → Reflect → Evolve
- Code Security behavioral spec: "Never introduce hardcoded secrets"
- Real scenario: Database connection with secret management
- Complete workflow from agent execution to prompt evolution

This is the **recommended starting point** for understanding how CodeOptiX works in practice.

## Behavioral Spec Scenarios

CodeOptiX supports various behavioral spec scenarios:

### 🔐 Code Security
- "Never introduce hardcoded secrets"
- "Do not disable auth checks"
- "Avoid insecure crypto patterns"

**Example:** `behavioral_spec_example.py` demonstrates the "hardcoded secrets" spec.

### 🧪 Test Generation
- "Tests must fail before fix"
- "Avoid vacuous assertions"
- "Include edge cases and negative tests"

### 🔁 Refactoring
- "Do not change public APIs without notice"
- "Preserve backward compatibility"
- "Avoid unnecessary churn"

### 📐 Planning & Requirements
- "Validate code changes against planning.md"
- "Surface deviations explicitly"
- "Ask for clarification when ambiguity exists"

### ⚙️ Infra / DevOps
- "Never expose public ports by default"
- "Require explicit approval for prod changes"
- "Prefer least-privilege defaults"

## Running Examples

### Prerequisites

1. Install dependencies:
```bash
pip install -e ".[dev,docs]"
# Or with uv:
uv sync --dev --extra docs
```

2. Set API keys (at least one):
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

### Run Examples

```bash
# Quick start with single behavior
python examples/quickstart-single-behavior.py

# Basic adapter usage
python examples/basic_adapter_usage.py

# Complete behavioral spec example (recommended)
python examples/behavioral_spec_example.py
```

## Configuration Files

The `configs/` directory contains example configuration files:

- `basic.yaml` - Basic configuration
- `ci-cd.yaml` - CI/CD pipeline configuration
- `single-behavior-insecure-code.yaml` - Single behavior evaluation
- `single-behavior-plan-drift.yaml` - Plan drift detection
- `single-behavior-vacuous-tests.yaml` - Test quality evaluation

## Creating Custom Behavior Specs

To create a custom behavior spec, see the [Behavior Specs documentation](../docs/concepts/behaviors.md).

Example structure:

```python
from codeoptix.behaviors.base import BehaviorSpec, BehaviorResult, Severity

class MyCustomBehavior(BehaviorSpec):
    name = "my-custom-behavior"
    description = "My custom behavior description"
    
    def evaluate(self, agent_output, context, llm_client=None):
        # Your evaluation logic
        return BehaviorResult(
            behavior_name=self.name,
            passed=True,
            score=0.9,
            severity=Severity.LOW,
            evidence=["Evidence 1", "Evidence 2"]
        )
```

## Next Steps

1. Run `quickstart-single-behavior.py` for a quick introduction
2. Run `behavioral_spec_example.py` to see the full workflow
3. Modify the examples to test your own scenarios
4. Create custom behavior specs for your use cases
5. Integrate CodeOptiX into your CI/CD pipeline using the config files
