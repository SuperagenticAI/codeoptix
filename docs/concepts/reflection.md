# Reflection Engine

The Reflection Engine analyzes evaluation results and generates human-readable insights about agent behavior.

---

## What is Reflection?

Reflection is the process of **understanding** why an agent behaved the way it did. It transforms raw evaluation results into actionable insights.

---

## How Reflection Works

### 1. Analyze Results

The engine analyzes evaluation results:

```python
reflection = reflection_engine.reflect(results)
```

### 2. Identify Patterns

It identifies patterns in failures:

- Common failure modes
- Root causes
- Evidence patterns

### 3. Generate Insights

It generates human-readable insights:

- Summary of issues
- Root cause analysis
- Recommendations

---

## Using the Reflection Engine

### Basic Usage

```python
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager

# Create artifact manager
artifact_manager = ArtifactManager()

# Create reflection engine
reflection_engine = ReflectionEngine(artifact_manager)

# Generate reflection
reflection = reflection_engine.reflect(
    results=evaluation_results,
    agent_name="codex"
)

print(reflection)
```

### Save Reflection

```python
reflection = reflection_engine.reflect(
    results=evaluation_results,
    agent_name="codex",
    save=True  # Saves to .codeoptix/artifacts/reflection_*.md
)
```

### From Run ID

```python
reflection = reflection_engine.reflect_from_run_id(
    run_id="abc123",
    agent_name="codex"
)
```

---

## Reflection Report Structure

The reflection report includes:

### 1. Summary

Overall evaluation summary:

```markdown
# Reflection Report

## Summary
The evaluation identified security issues in the agent's code generation.
Overall score: 0.65/1.0
```

### 2. Root Causes

Why issues occurred:

```markdown
## Root Causes
1. Agent lacks explicit instructions to avoid hardcoded secrets
2. No validation for secure coding practices
3. Missing examples of secure code patterns
```

### 3. Evidence

Specific examples:

```markdown
## Evidence
- Hardcoded password found at line 5 in scenario 1
- SQL injection risk in scenario 2
- Missing input validation in scenario 3
```

### 4. Recommendations

How to improve:

```markdown
## Recommendations
1. Add explicit security guidelines to agent prompt
2. Include examples of secure code patterns
3. Add validation checks in behavior specifications
```

---

## Configuration

```python
config = {
    "generator": {
        "detail_level": "high",  # "low", "medium", "high"
        "include_evidence": True,
        "include_recommendations": True
    }
}

reflection_engine = ReflectionEngine(artifact_manager, config=config)
```

---

## Best Practices

### 1. Always Reflect

Always generate reflection after evaluation:

```python
results = engine.evaluate_behaviors(...)
reflection = reflection_engine.reflect(results)
```

### 2. Review Reflection

Read the reflection report to understand issues:

```python
reflection = reflection_engine.reflect(results, save=True)
# Review .codeoptix/artifacts/reflection_*.md
```

### 3. Use for Evolution

Use reflection for prompt evolution:

```python
reflection = reflection_engine.reflect(results)
evolved = evolution_engine.evolve(results, reflection)
```

---

## Integration with Evolution

Reflection is used by the Evolution Engine to improve prompts:

```python
# 1. Evaluate
results = engine.evaluate_behaviors(...)

# 2. Reflect
reflection = reflection_engine.reflect(results)

# 3. Evolve
evolved = evolution_engine.evolve(results, reflection)
```

---

## Next Steps

- [Evolution Engine](evolution.md) - Use reflection to improve agents
- [Python API Guide](../guides/python-api.md) - Advanced usage
- [CLI Usage](../guides/cli-usage.md) - Command-line usage

