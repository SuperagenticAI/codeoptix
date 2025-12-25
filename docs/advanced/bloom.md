# Bloom Integration

CodeOptiX uses Bloom for sophisticated scenario generation in evaluations.

---

## What is Bloom?

Bloom is an open-source framework for automated behavior evaluation of LLMs. CodeOptiX integrates Bloom's ideation patterns for scenario generation.

---

## Bloom in CodeOptiX

### Lightweight Integration

CodeOptiX uses Bloom-style patterns by default:

```python
config = {
    "scenario_generator": {
        "use_bloom": True  # Default
    }
}
```

### Full Bloom Integration

Enable full Bloom integration for advanced scenario generation:

```python
config = {
    "scenario_generator": {
        "use_bloom": True,
        "use_full_bloom": True,  # Full Bloom integration
        "num_base_scenarios": 3,
        "num_variations": 2
    }
}
```

---

## How Bloom Works

### 1. Ideation

Bloom generates base scenarios using ideation prompts:

```python
from codeoptix.evaluation.bloom_integration import BloomIdeationIntegration

bloom = BloomIdeationIntegration(llm_client, config)
scenarios = bloom.generate_scenarios(
    behavior_name="insecure-code",
    behavior_description="Detect insecure code"
)
```

### 2. Variation

Bloom creates variations of base scenarios:

```python
variations = bloom._generate_variations(
    base_scenario=scenario,
    behavior_name="insecure-code",
    behavior_description="Detect insecure code"
)
```

---

## Using Bloom

### Enable Bloom

```python
config = {
    "scenario_generator": {
        "use_bloom": True,
        "use_full_bloom": True
    }
}

engine = EvaluationEngine(adapter, llm_client, config=config)
```

### Bloom Configuration

```python
config = {
    "scenario_generator": {
        "use_bloom": True,
        "use_full_bloom": True,
        "num_base_scenarios": 5,
        "num_variations": 3,
        "model": "gpt-4o"
    }
}
```

---

## Bloom Scenario Generation

### Base Scenarios

Bloom generates diverse base scenarios:

```python
base_scenarios = bloom._generate_base_scenarios(
    behavior_name="insecure-code",
    behavior_description="Detect insecure code",
    examples=[]
)
```

### Variations

Bloom creates variations for each base scenario:

```python
for base_scenario in base_scenarios:
    variations = bloom._generate_variations(
        base_scenario=base_scenario,
        behavior_name="insecure-code",
        behavior_description="Detect insecure code"
    )
```

---

## Vendored Bloom Components

CodeOptiX includes vendored Bloom components:

- `codeoptix.vendor.bloom.scripts.step2_ideation` - Ideation scripts
- `codeoptix.vendor.bloom.prompts.step2_ideation` - Ideation prompts
- `codeoptix.vendor.bloom.utils` - Bloom utilities

---

## Example

```python
from codeoptix.evaluation import EvaluationEngine

config = {
    "scenario_generator": {
        "use_bloom": True,
        "use_full_bloom": True,
        "num_scenarios": 5
    }
}

engine = EvaluationEngine(adapter, llm_client, config=config)
results = engine.evaluate_behaviors(["insecure-code"])
```

---

## Best Practices

### 1. Use Full Bloom for Complex Behaviors

For complex behaviors, use full Bloom:

```python
config = {
    "scenario_generator": {
        "use_full_bloom": True
    }
}
```

### 2. Adjust Scenario Count

Balance between coverage and speed:

```python
config = {
    "scenario_generator": {
        "num_scenarios": 3  # Good balance
    }
}
```

### 3. Provide Examples

Provide example scenarios for better generation:

```python
scenarios = engine.evaluate_behaviors(
    behavior_names=["insecure-code"],
    scenarios=example_scenarios  # Provide examples
)
```

---

## Troubleshooting

### Bloom Not Working

Check configuration:

```python
config = {
    "scenario_generator": {
        "use_bloom": True  # Must be enabled
    }
}
```

### Too Many Scenarios

Reduce scenario count:

```python
config = {
    "scenario_generator": {
        "num_scenarios": 2  # Reduce count
    }
}
```

---

## Next Steps

- [Evaluation Engine](../concepts/evaluation.md) - Learn about evaluation
- [GEPA Integration](gepa.md) - Prompt evolution
- [Error Handling](error-handling.md) - Handle errors

