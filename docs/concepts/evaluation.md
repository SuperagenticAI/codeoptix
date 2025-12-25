# Evaluation Engine

The Evaluation Engine orchestrates the entire evaluation process, from scenario generation to result aggregation.

---

## What is the Evaluation Engine?

The Evaluation Engine is the **core component** that:
- Generates test scenarios
- Executes your agent
- Runs behavior evaluations
- Aggregates results

---

## How It Works

### 1. Scenario Generation

The engine generates test scenarios for each behavior:

```python
scenarios = generator.generate_scenarios(
    behavior_name="insecure-code",
    behavior_description="Detect insecure code"
)
```

### 2. Agent Execution

Your agent runs on each scenario:

```python
for scenario in scenarios:
    output = adapter.execute(scenario["prompt"])
```

### 3. Behavior Evaluation

Each behavior evaluates the agent output:

```python
result = behavior.evaluate(output, context=scenario.get("context"))
```

### 4. Result Aggregation

Results are aggregated into a final report:

```python
overall_score = sum(scores) / len(scores)
```

---

## Using the Evaluation Engine

### Basic Usage

```python
from codeoptix.evaluation import EvaluationEngine
from codeoptix.adapters.factory import create_adapter
from codeoptix.utils.llm import create_llm_client, LLMProvider

# Create adapter
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})

# Create LLM client
llm_client = create_llm_client(LLMProvider.OPENAI)

# Create evaluation engine
engine = EvaluationEngine(adapter, llm_client)

# Evaluate behaviors
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code", "vacuous-tests"]
)
```

### With Configuration

```python
config = {
    "scenario_generator": {
        "num_scenarios": 5,
        "use_bloom": True,
        "use_full_bloom": True
    },
    "static_analysis": {
        "bandit": True
    },
    "test_runner": {
        "coverage": True
    }
}

engine = EvaluationEngine(adapter, llm_client, config=config)
```

### With Context

```python
context = {
    "plan": "Create secure authentication API",
    "requirements": [
        "Use JWT tokens",
        "Hash passwords",
        "No hardcoded secrets"
    ]
}

results = engine.evaluate_behaviors(
    behavior_names=["insecure-code", "plan-drift"],
    context=context
)
```

---

## Results Structure

The evaluation engine returns a comprehensive results dictionary:

```python
{
    "run_id": "abc123",
    "timestamp": "2025-01-20T10:00:00Z",
    "agent": "codex",
    "overall_score": 0.75,
    "behaviors": {
        "insecure-code": {
            "behavior_name": "insecure-code",
            "scenarios_tested": 3,
            "scenarios_passed": 2,
            "score": 0.75,
            "passed": True,
            "evidence": ["Hardcoded password found"],
            "scenario_results": [...]
        }
    },
    "scenarios": [...],
    "metadata": {...}
}
```

---

## Scenario Generation

### Bloom Integration

CodeOptiX uses Bloom for sophisticated scenario generation:

```python
config = {
    "scenario_generator": {
        "use_bloom": True,
        "use_full_bloom": True,  # Full Bloom integration
        "num_scenarios": 5,
        "num_variations": 2
    }
}
```

### Custom Scenarios

You can provide pre-generated scenarios:

```python
scenarios = [
    {
        "prompt": "Write a function to connect to a database",
        "task": "Database connection",
        "behavior": "insecure-code"
    }
]

results = engine.evaluate_behaviors(
    behavior_names=["insecure-code"],
    scenarios=scenarios
)
```

---

## Multi-Modal Evaluation

The evaluation engine uses multiple evaluation signals:

### 1. Behavior Specs

Primary evaluation using behavior specifications.

### 2. Static Analysis

Uses tools like Bandit for security analysis.

### 3. Test Execution

Runs tests and checks coverage.

### 4. LLM Evaluation

Semantic analysis using LLMs.

### 5. Artifact Comparison

Compares code against planning artifacts.

---

## Configuration Options

### Scenario Generator

```python
"scenario_generator": {
    "num_scenarios": 3,        # Number of scenarios per behavior
    "use_bloom": True,         # Use Bloom-style generation
    "use_full_bloom": True,    # Full Bloom integration
    "num_variations": 2,       # Variations per scenario
    "model": "gpt-4o"         # LLM model for generation
}
```

### Static Analysis

```python
"static_analysis": {
    "bandit": True  # Enable Bandit security checks
}
```

### Test Runner

```python
"test_runner": {
    "coverage": True  # Enable coverage analysis
}
```

### LLM Evaluator

```python
"llm_evaluator": {
    "model": "gpt-4o",
    "temperature": 0.3
}
```

---

## Best Practices

### 1. Start with Few Scenarios

Begin with a small number of scenarios:

```python
config = {
    "scenario_generator": {
        "num_scenarios": 2  # Start small
    }
}
```

### 2. Use Relevant Behaviors

Only evaluate behaviors relevant to your use case:

```python
behaviors = ["insecure-code"]  # Focus on what matters
```

### 3. Provide Context

Always provide context when available:

```python
results = engine.evaluate_behaviors(
    behavior_names=["plan-drift"],
    context={"plan": plan_content}
)
```

### 4. Review Results

Always review the detailed results:

```python
for behavior_name, behavior_data in results["behaviors"].items():
    print(f"{behavior_name}: {behavior_data['score']:.2f}")
    for evidence in behavior_data["evidence"]:
        print(f"  - {evidence}")
```

---

## Error Handling

The evaluation engine handles errors gracefully:

- **API failures**: Retries with exponential backoff
- **Parsing errors**: Falls back to default scenarios
- **Agent errors**: Continues with other scenarios

---

## Performance Tips

### 1. Parallel Execution

The engine can evaluate multiple scenarios in parallel (when supported).

### 2. Caching

Results are cached to avoid redundant evaluations.

### 3. Minibatch Evaluation

Use minibatches for faster iteration:

```python
config = {
    "scenario_generator": {
        "num_scenarios": 2  # Smaller batches
    }
}
```

---

## Next Steps

- [Reflection Engine](reflection.md) - Understand results
- [Evolution Engine](evolution.md) - Improve agents
- [Python API Guide](../guides/python-api.md) - Advanced usage

