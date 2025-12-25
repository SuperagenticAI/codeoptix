# API Reference

Complete API reference for CodeOptiX.

---

## Agent Adapters

### `create_adapter(adapter_type: str, config: Dict[str, Any]) -> AgentAdapter`

Create an agent adapter.

**Parameters:**
- `adapter_type`: One of `"claude-code"`, `"codex"`, `"gemini-cli"`
- `config`: Configuration dictionary

**Returns:**
- `AgentAdapter` instance

**Example:**
```python
from codeoptix.adapters.factory import create_adapter

adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": "sk-...",
    }
})
```

---

## Evaluation Engine

### `EvaluationEngine`

Main orchestrator for behavioral evaluation.

#### `__init__(adapter, llm_client, config=None)`

Initialize evaluation engine.

**Parameters:**
- `adapter`: Agent adapter instance
- `llm_client`: LLM client instance
- `config`: Optional configuration dictionary

#### `evaluate_behaviors(behavior_names, scenarios=None, context=None) -> Dict`

Evaluate agent against behaviors.

**Parameters:**
- `behavior_names`: List of behavior names
- `scenarios`: Optional pre-generated scenarios
- `context`: Optional context dictionary

**Returns:**
- Results dictionary

**Example:**
```python
from codeoptix.evaluation import EvaluationEngine

engine = EvaluationEngine(adapter, llm_client)
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code"],
    context={"plan": "Create secure API"}
)
```

---

## Behavior Specifications

### `create_behavior(name: str, config: Optional[Dict] = None) -> BehaviorSpec`

Create a behavior specification.

**Parameters:**
- `name`: Behavior name - one of: **`"insecure-code"`**, **`"vacuous-tests"`**, or **`"plan-drift"`**
- `config`: Optional configuration

**Returns:**
- `BehaviorSpec` instance

**Example:**
```python
from codeoptix.behaviors import create_behavior

behavior = create_behavior("insecure-code")
result = behavior.evaluate(agent_output)
```

---

## Reflection Engine

### `ReflectionEngine`

Generates reflection reports.

#### `__init__(artifact_manager=None, config=None)`

Initialize reflection engine.

#### `reflect(results, agent_name=None, save=True) -> str`

Generate reflection from results.

**Returns:**
- Reflection markdown string

**Example:**
```python
from codeoptix.reflection import ReflectionEngine

engine = ReflectionEngine(artifact_manager)
reflection = engine.reflect(results)
```

---

## Evolution Engine

### `EvolutionEngine`

Optimizes agent prompts.

#### `__init__(adapter, evaluation_engine, llm_client, artifact_manager=None, config=None)`

Initialize evolution engine.

#### `evolve(evaluation_results, reflection, behavior_names=None, context=None) -> Dict`

Evolve agent prompts.

**Returns:**
- Evolved prompts dictionary

**Example:**
```python
from codeoptix.evolution import EvolutionEngine

engine = EvolutionEngine(adapter, eval_engine, llm_client)
evolved = engine.evolve(results, reflection)
```

---

## Artifact Manager

### `ArtifactManager`

Manages evaluation artifacts.

#### `save_results(results, run_id=None) -> Path`

Save evaluation results.

#### `load_results(run_id) -> Dict`

Load evaluation results.

#### `save_reflection(reflection_content, run_id=None) -> Path`

Save reflection report.

#### `list_runs() -> List[Dict]`

List all evaluation runs.

---

## LLM Client

### `create_llm_client(provider, api_key=None) -> LLMClient`

Create an LLM client.

**Parameters:**
- `provider`: `LLMProvider.OPENAI`, `LLMProvider.ANTHROPIC`, or `LLMProvider.GOOGLE`
- `api_key`: Optional API key

**Example:**
```python
from codeoptix.utils.llm import create_llm_client, LLMProvider

client = create_llm_client(LLMProvider.OPENAI, api_key="sk-...")
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-5.2"
)
```

---

## Error Handling

### `retry_llm_call(max_attempts=3, initial_wait=1.0, max_wait=60.0)`

Retry decorator for LLM calls.

**Example:**
```python
from codeoptix.utils.retry import retry_llm_call

@retry_llm_call(max_attempts=3)
def call_api():
    # Your API call
    pass
```

---

For more details, see the [full API documentation](API.md).

