# GEPA Integration

CodeOptiX uses GEPA (Genetic-Pareto) to automatically improve agent prompts through reflective mutation.

---

## What is GEPA?

**GEPA (Genetic-Pareto)** is a framework for optimizing textual system components (like AI prompts, code, or instructions) using LLM-based reflection and evolutionary search. GEPA employs iterative mutation, reflection, and Pareto-aware candidate selection to evolve robust, high-performing variants.

**Note**: CodeOptiX uses GEPA's `InstructionProposalSignature` component for prompt evolution. This is a minimal integration that uses GEPA's proven instruction proposal mechanism, rather than the full GEPA optimization framework.

---

## How GEPA Works in CodeOptiX

### 1. Reflective Dataset

GEPA uses evaluation failures to create a reflective dataset:

```python
reflective_dataset = [
    {
        "behavior": "insecure-code",
        "score": 0.5,
        "evidence": ["Hardcoded password found"],
        "scenario": "Write database connection code"
    }
]
```

### 2. Instruction Proposal

GEPA's `InstructionProposalSignature` generates improved prompts:

```python
from gepa.strategies.instruction_proposal import InstructionProposalSignature

result = InstructionProposalSignature.run(
    lm=llm_client,
    input_dict={
        "current_instruction_doc": current_prompt,
        "dataset_with_feedback": reflective_dataset,
    }
)

new_prompt = result["new_instruction"]
```

### 3. Iterative Improvement

The process repeats until no improvement is found.

---

## Using GEPA in CodeOptiX

### Enable GEPA

GEPA is enabled by default in the Evolution Engine:

```python
config = {
    "proposer": {
        "use_gepa": True,  # Default
        "model": "gpt-5.2"
    }
}

evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager, config=config
)
```

### GEPA Configuration

```python
config = {
    "proposer": {
        "use_gepa": True,
        "model": "gpt-5.2",
        "temperature": 0.7,
        "prompt_template": "custom_template"  # Optional
    }
}
```

---

## GEPA Integration Details

### MinimalGEPAProposer

CodeOptiX uses `MinimalGEPAProposer` which wraps GEPA's `InstructionProposalSignature`:

```python
from codeoptix.evolution.gepa_integration import MinimalGEPAProposer

proposer = MinimalGEPAProposer(llm_client, config)
improved_prompt = proposer.propose_improved_prompt(
    current_prompt=current_prompt,
    reflective_dataset=reflective_dataset
)
```

### Data Format Conversion

CodeOptiX converts its format to GEPA's expected format:

```python
gepa_dataset = [
    {
        "Inputs": {
            "task": scenario["prompt"],
            "behavior": behavior_name
        },
        "Generated Outputs": {
            "score": score,
            "evidence": evidence
        },
        "Feedback": feedback_string
    }
]
```

---

## Example: GEPA Evolution

```python
from codeoptix.evolution import EvolutionEngine

# Initialize with GEPA enabled
config = {
    "max_iterations": 3,
    "proposer": {
        "use_gepa": True
    }
}

evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager, config=config
)

# Evolve using GEPA
evolved = evolution_engine.evolve(
    evaluation_results=results,
    reflection=reflection_content
)

print(evolved["prompts"]["system_prompt"])
```

---

## GEPA vs Custom Implementation

### GEPA (Default)

- Uses proven GEPA framework
- LLM-based prompt generation
- Handles complex patterns

### Custom Implementation

Disable GEPA to use custom logic:

```python
config = {
    "proposer": {
        "use_gepa": False  # Use custom implementation
    }
}
```

---

## Best Practices

### 1. Provide Good Reflection

Better reflection leads to better evolution:

```python
reflection = reflection_engine.reflect(results)
evolved = evolution_engine.evolve(results, reflection)
```

### 2. Use Appropriate LLM

GEPA works best with capable models:

```python
config = {
    "proposer": {
        "use_gepa": True,
        "model": "gpt-5.2"  # Use capable model
    }
}
```

### 3. Iterate Gradually

Start with few iterations:

```python
config = {
    "max_iterations": 2  # Start small
}
```

---

## Troubleshooting

### GEPA Not Working

Check that GEPA is enabled:

```python
config = {
    "proposer": {
        "use_gepa": True  # Must be True
    }
}
```

### No Improvement

GEPA may not find improvement if:
- Initial prompt is already good
- Failures are not pattern-based
- LLM cannot identify improvements

---

## Next Steps

- [Evolution Engine](../concepts/evolution.md) - Learn about evolution
- [Bloom Integration](bloom.md) - Scenario generation
- [Error Handling](error-handling.md) - Handle errors

