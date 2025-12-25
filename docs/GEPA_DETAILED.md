# GEPA Integration - Detailed Explanation

## When and Where GEPA is Used

GEPA is used in the **Evolution Engine** when evolving agent prompts. Specifically:

1. **Location**: `src/codeoptix/evolution/gepa_integration.py`
2. **When**: During the `evolve()` method in `EvolutionEngine`
3. **Purpose**: To propose improved prompts based on evaluation failures

## How GEPA Does Optimization

### The Flow

```
1. Evaluation Results (failures)
   ↓
2. Build Reflective Dataset (failure examples)
   ↓
3. GEPA's InstructionProposalSignature
   ↓
4. LLM generates improved prompt
   ↓
5. Test improved prompt on minibatch
   ↓
6. Select best candidate
   ↓
7. Iterate (up to max_iterations)
```

### Step-by-Step Process

#### Step 1: Evaluation Results
```python
# After evaluation, we have:
{
    "behaviors": {
        "insecure-code": {
            "score": 0.3,  # Failed!
            "evidence": ["Hardcoded API key found"],
            "scenario_results": [...]
        }
    }
}
```

#### Step 2: Build Reflective Dataset
```python
# CodeOptiX converts failures to reflective dataset:
reflective_data = [
    {
        "behavior": "insecure-code",
        "score": 0.3,
        "evidence": ["Hardcoded API key found"],
        "scenario": "Create a database connection..."
    }
]
```

#### Step 3: GEPA Format Conversion
```python
# GEPA expects this format:
gepa_dataset = [
    {
        "Inputs": {
            "task": "Create a database connection...",
            "behavior": "insecure-code"
        },
        "Generated Outputs": {
            "score": 0.3,
            "evidence": ["Hardcoded API key found"]
        },
        "Feedback": "Behavior 'insecure-code' scored 0.30/1.0. Issues found: Hardcoded API key found"
    }
]
```

#### Step 4: GEPA's InstructionProposalSignature
```python
# GEPA uses its InstructionProposalSignature to:
# 1. Build a prompt template with:
#    - Current instruction (prompt)
#    - Reflective dataset (failure examples)
#    - Feedback on each failure
#
# 2. Call LLM with this template
result = InstructionProposalSignature.run(
    lm=llm_client,  # Wrapped CodeOptiX LLM client
    input_dict={
        "current_instruction_doc": current_prompt,
        "dataset_with_feedback": gepa_dataset,
        "prompt_template": gepa_template,
    }
)

# 3. Extract improved prompt
improved_prompt = result["new_instruction"]
```

#### Step 5: Test and Select
```python
# Evolution engine:
# 1. Generates population of candidates (using GEPA)
# 2. Tests each on minibatch (2-3 scenarios)
# 3. Selects best performing
# 4. Iterates if improvement found
```

## Which LLM is Used

### LLM Selection

The LLM used for GEPA is **the same LLM client passed to EvolutionEngine**:

```python
# When creating EvolutionEngine:
llm_client = create_llm_client(LLMProvider.OPENAI, api_key=...)
evolution_engine = EvolutionEngine(
    adapter=adapter,
    evaluation_engine=eval_engine,
    llm_client=llm_client,  # ← This LLM is used by GEPA
    ...
)
```

### LLM Wrapper

CodeOptiX wraps its LLM client to match GEPA's interface:

```python
class GEPALLMWrapper:
    def __call__(self, prompt: str) -> str:
        """GEPA calls this with the instruction proposal prompt."""
        return self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",  # or whatever model is configured
            temperature=0.7,
        )
```

### Default Model

- **Default**: `gpt-4o` (if using OpenAI)
- **Configurable**: Via `llm_client` configuration
- **Temperature**: 0.7 (for creative prompt proposals)

## How It's Demonstrated

### Example 1: Basic Evolution (CLI)

```bash
# 1. Run evaluation
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai \
  --output results.json

# 2. Generate reflection
codeoptix reflect --input results.json

# 3. Evolve prompts (GEPA is used here!)
codeoptix evolve \
  --input results.json \
  --iterations 3 \
  --llm-provider openai
```

### Example 2: Python API

```python
from codeoptix.evolution import EvolutionEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

# Create LLM client (this will be used by GEPA)
llm_client = create_llm_client(
    LLMProvider.OPENAI,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create evolution engine
evolution_engine = EvolutionEngine(
    adapter=adapter,
    evaluation_engine=eval_engine,
    llm_client=llm_client,  # ← GEPA uses this
    config={
        "max_iterations": 3,
        "population_size": 3,
        "proposer": {
            "use_gepa": True,  # ← Enable GEPA (default)
        }
    }
)

# Evolve (GEPA is called internally)
evolved = evolution_engine.evolve(
    evaluation_results=results,
    reflection=reflection_content
)
```

### Example 3: Direct GEPA Usage

```python
from codeoptix.evolution.gepa_integration import MinimalGEPAProposer
from codeoptix.utils.llm import create_llm_client, LLMProvider

# Create LLM client
llm_client = create_llm_client(LLMProvider.OPENAI)

# Create GEPA proposer
gepa_proposer = MinimalGEPAProposer(llm_client)

# Current prompt (failing)
current_prompt = "You are a helpful coding assistant."

# Reflective dataset (failures)
reflective_data = [
    {
        "behavior": "insecure-code",
        "score": 0.3,
        "evidence": ["Hardcoded API key found"],
        "scenario": "Create database connection"
    }
]

# GEPA proposes improved prompt
improved_prompt = gepa_proposer.propose_improved_prompt(
    current_prompt=current_prompt,
    reflective_dataset=reflective_data,
    component_name="system_prompt"
)

print(f"Improved: {improved_prompt}")
```

## GEPA's Role in Optimization

### What GEPA Does

1. **Reflective Mutation**: Uses failure examples to propose improvements
2. **Instruction Proposal**: Generates new prompt text that addresses failures
3. **Template-Based**: Uses proven prompt templates for instruction evolution

### What GEPA Doesn't Do

- ❌ Candidate selection (CodeOptiX does this)
- ❌ Population management (CodeOptiX does this)
- ❌ Fitness evaluation (CodeOptiX's evaluation engine does this)
- ❌ Iteration control (CodeOptiX's evolution engine does this)

### CodeOptiX's Role

CodeOptiX orchestrates the evolution:
- Generates population of candidates (using GEPA for each)
- Tests candidates on minibatch
- Selects best performing
- Iterates if improvement found

## Configuration

### Enable/Disable GEPA

```python
# Enable GEPA (default)
config = {
    "proposer": {
        "use_gepa": True,  # ← Uses GEPA
    }
}

# Disable GEPA (use custom implementation)
config = {
    "proposer": {
        "use_gepa": False,  # ← Uses custom prompt proposal
    }
}
```

### GEPA-Specific Config

```python
config = {
    "proposer": {
        "use_gepa": True,
        "prompt_template": None,  # Use GEPA default
        # Or provide custom template
    }
}
```

## LLM Usage Summary

| Component | LLM Used | Purpose |
|-----------|----------|---------|
| **Agent Adapter** | Configured in adapter | Generate code |
| **Evaluation Engine** | Configured in eval | Judge behavior |
| **Reflection Engine** | Configured in reflection | Generate insights |
| **GEPA (Evolution)** | Same as EvolutionEngine | Propose improved prompts |

**Key Point**: GEPA uses the **same LLM client** passed to `EvolutionEngine`, which is typically the same one used for evaluation and reflection.

## Example: Full Workflow

```python
# 1. Setup
llm_client = create_llm_client(LLMProvider.OPENAI)

# 2. Evaluate
eval_engine = EvaluationEngine(adapter, llm_client)
results = eval_engine.evaluate_behaviors(["insecure-code"])

# 3. Reflect
reflection_engine = ReflectionEngine()
reflection = reflection_engine.reflect(results)

# 4. Evolve (GEPA is used here!)
evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client,
    config={"proposer": {"use_gepa": True}}
)
evolved = evolution_engine.evolve(results, reflection)

# GEPA's work:
# - Takes current prompt: "You are a helpful assistant"
# - Takes failures: [{"behavior": "insecure-code", "score": 0.3, ...}]
# - Uses InstructionProposalSignature to generate:
#   "You are a helpful assistant. Always use environment variables for secrets..."
```

## Debugging GEPA

To see GEPA in action:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# GEPA will log:
# - Prompt template being used
# - LLM calls being made
# - Proposed instructions
```

## Summary

- **When**: During prompt evolution (`EvolutionEngine.evolve()`)
- **Where**: `MinimalGEPAProposer.propose_improved_prompt()`
- **How**: Uses GEPA's `InstructionProposalSignature` with reflective dataset
- **LLM**: Same LLM client passed to `EvolutionEngine` (default: OpenAI GPT-4o)
- **Purpose**: Generate improved prompts that address evaluation failures

