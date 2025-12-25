# GEPA Demonstration

Example showing how GEPA optimizes agent prompts.

---

## Overview

This example demonstrates the complete GEPA evolution process.

---

## Complete Code

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.evolution import EvolutionEngine
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager
from codeoptix.utils.llm import create_llm_client, LLMProvider

# 1. Setup
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})

llm_client = create_llm_client(LLMProvider.OPENAI)
artifact_manager = ArtifactManager()

# 2. Initial evaluation
eval_engine = EvaluationEngine(adapter, llm_client)
results = eval_engine.evaluate_behaviors(
    behavior_names=["insecure-code"]
)

print(f"Initial Score: {results['overall_score']:.2f}")

# 3. Reflect
reflection_engine = ReflectionEngine(artifact_manager)
reflection = reflection_engine.reflect(results)

# 4. Evolve with GEPA
evolution_config = {
    "max_iterations": 2,
    "proposer": {
        "use_gepa": True  # Enable GEPA
    }
}

evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager, config=evolution_config
)

evolved = evolution_engine.evolve(
    evaluation_results=results,
    reflection=reflection,
    behavior_names=["insecure-code"]
)

# 5. Results
print(f"Final Score: {evolved['metadata']['final_score']:.2f}")
print(f"Improvement: {evolved['metadata']['improvement']:.2f}")
print(f"\nEvolved Prompt:\n{evolved['prompts']['system_prompt']}")
```

---

## Running the Example

```bash
export OPENAI_API_KEY="sk-..."
python examples/gepa_demonstration.py
```

---

## Expected Output

```
Initial Score: 0.65
🧬 Evolving prompts with GEPA...
Final Score: 0.85
Improvement: 0.20

Evolved Prompt:
You are a security-focused coding assistant. Never include hardcoded secrets...
```

---

## Next Steps

- [GEPA Integration](../advanced/gepa.md) - Learn about GEPA
- [Evolution Engine](../concepts/evolution.md) - Evolution details
- [Python API Guide](../guides/python-api.md) - More examples

