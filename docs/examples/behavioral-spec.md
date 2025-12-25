# Behavioral Spec Example

Complete example of using CodeOptiX to evaluate agent behavior.

---

## Overview

This example demonstrates evaluating an agent for security issues.

---

## Complete Code

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
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

# 2. Evaluate
eval_engine = EvaluationEngine(adapter, llm_client)
results = eval_engine.evaluate_behaviors(
    behavior_names=["insecure-code"]
)

# 3. Save results
artifact_manager.save_results(results)

# 4. Reflect
reflection_engine = ReflectionEngine(artifact_manager)
reflection = reflection_engine.reflect(results, save=True)

# 5. Print summary
print(f"Overall Score: {results['overall_score']:.2f}")
for behavior_name, behavior_data in results['behaviors'].items():
    status = "✅ PASSED" if behavior_data['passed'] else "❌ FAILED"
    print(f"{behavior_name}: {status} (Score: {behavior_data['score']:.2f})")
```

---

## Running the Example

```bash
export OPENAI_API_KEY="sk-..."
python examples/behavioral_spec_example.py
```

---

## Expected Output

```
Overall Score: 0.75
insecure-code: ❌ FAILED (Score: 0.75)
  - Hardcoded password found at line 5
```

---

## Next Steps

- [GEPA Demo](gepa-demo.md) - GEPA evolution example
- [Adapter Usage](adapter-usage.md) - Adapter examples
- [Python API Guide](../guides/python-api.md) - More examples

