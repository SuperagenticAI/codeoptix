# Evolution Engine

The Evolution Engine automatically improves agent prompts using GEPA-style optimization based on evaluation results.

---

## What is Evolution?

Evolution is the process of **automatically improving** agent prompts based on evaluation results. It uses GEPA (Genetic-Pareto) to generate better prompts through reflective mutation.

---

## How Evolution Works

### 1. Analyze Failures

The engine analyzes evaluation failures:

```python
failures = extract_failures(evaluation_results)
```

### 2. Generate Proposals

It generates improved prompt proposals using GEPA:

```python
proposed_prompt = gepa_proposer.propose_improved_prompt(
    current_prompt=current_prompt,
    reflective_dataset=failures
)
```

### 3. Test Candidates

It tests candidate prompts:

```python
for candidate in candidates:
    score = evaluate_candidate(candidate)
```

### 4. Select Best

It selects the best-performing prompt:

```python
best_prompt = select_best(candidates, scores)
```

---

## Using the Evolution Engine

### Basic Usage

```python
from codeoptix.evolution import EvolutionEngine
from codeoptix.evaluation import EvaluationEngine
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager

# Create engines
eval_engine = EvaluationEngine(adapter, llm_client)
reflection_engine = ReflectionEngine(artifact_manager)
artifact_manager = ArtifactManager()

# Create evolution engine
evolution_engine = EvolutionEngine(
    adapter=adapter,
    evaluation_engine=eval_engine,
    llm_client=llm_client,
    artifact_manager=artifact_manager
)

# Evolve prompts
evolved = evolution_engine.evolve(
    evaluation_results=results,
    reflection=reflection_content,
    behavior_names=["insecure-code"]
)
```

### With Configuration

```python
config = {
    "max_iterations": 3,      # Number of evolution iterations
    "population_size": 3,     # Number of candidates per iteration
    "minibatch_size": 2,      # Scenarios per evaluation
    "improvement_threshold": 0.05,  # Minimum improvement to accept
    "proposer": {
        "use_gepa": True,     # Use GEPA for proposal
        "model": "gpt-5.2"
    }
}

evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager, config=config
)
```

---

## Evolution Process

### Iteration 1

1. Generate 3 candidate prompts
2. Evaluate each on minibatch
3. Select best candidate
4. If improved, accept; otherwise stop

### Iteration 2

1. Generate new candidates from best
2. Evaluate again
3. Continue until no improvement

### Final Result

Best prompt is saved and applied to adapter.

---

## Evolved Prompts Structure

```python
{
    "agent": "codex",
    "prompts": {
        "system_prompt": "Improved prompt text..."
    },
    "metadata": {
        "iterations": 2,
        "initial_score": 0.65,
        "final_score": 0.85,
        "improvement": 0.20,
        "evolution_history": [...]
    }
}
```

---

## GEPA Integration

The Evolution Engine uses GEPA for prompt proposal:

```python
config = {
    "proposer": {
        "use_gepa": True,  # Enable GEPA
        "model": "gpt-5.2"
    }
}
```

GEPA uses:
- **Reflective Dataset**: Failure examples
- **Instruction Proposal**: LLM-based prompt generation
- **Iterative Improvement**: Multiple refinement rounds

---

## Configuration Options

### Evolution Parameters

```python
{
    "max_iterations": 3,           # Maximum iterations
    "population_size": 3,           # Candidates per iteration
    "minibatch_size": 2,            # Scenarios per evaluation
    "improvement_threshold": 0.05   # Minimum improvement
}
```

### Proposer Configuration

```python
{
    "proposer": {
        "use_gepa": True,           # Use GEPA
        "model": "gpt-5.2",          # LLM model
        "temperature": 0.7         # Generation temperature
    }
}
```

---

## Best Practices

### 1. Start with Evaluation

Always evaluate before evolving:

```python
results = eval_engine.evaluate_behaviors(...)
```

### 2. Generate Reflection

Generate reflection for better evolution:

```python
reflection = reflection_engine.reflect(results)
```

### 3. Focus on Specific Behaviors

Evolve for specific behaviors:

```python
evolved = evolution_engine.evolve(
    results,
    reflection,
    behavior_names=["insecure-code"]  # Focus
)
```

### 4. Review Evolved Prompts

Always review evolved prompts:

```python
print(evolved["prompts"]["system_prompt"])
```

---

## Evolution History

The evolution history tracks progress:

```python
history = evolved["metadata"]["evolution_history"]

for iteration in history:
    print(f"Iteration {iteration['iteration']}:")
    print(f"  Score: {iteration['best_score']:.2f}")
    print(f"  Improvement: {iteration['improvement']:.2f}")
```

---

## Limitations

### 1. Iteration Limit

Evolution stops after `max_iterations` or when no improvement is found.

### 2. Minibatch Evaluation

Uses minibatch for speed, may not reflect full performance.

### 3. LLM Dependency

Requires LLM access for prompt generation.

---

## Next Steps

- [GEPA Integration](../advanced/gepa.md) - Learn about GEPA
- [Python API Guide](../guides/python-api.md) - Advanced usage
- [CLI Usage](../guides/cli-usage.md) - Command-line usage

