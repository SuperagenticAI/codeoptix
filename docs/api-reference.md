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

**Parameters:**
- `results`: Evaluation results dictionary
- `agent_name`: Optional agent name for report
- `save`: Whether to save reflection to file (default: True)

**Returns:**
- Reflection markdown string

**Example:**
```python
from codeoptix.reflection import ReflectionEngine

engine = ReflectionEngine(artifact_manager)
reflection = engine.reflect(results, agent_name="codex")
```

#### `reflect_from_run_id(run_id, agent_name=None) -> str`

Generate reflection from a saved run ID.

**Parameters:**
- `run_id`: Run ID string
- `agent_name`: Optional agent name for report

**Returns:**
- Reflection markdown string

**Example:**
```python
reflection = engine.reflect_from_run_id("run-001", agent_name="codex")
```

---

## Evolution Engine

### `EvolutionEngine`

Optimizes agent prompts.

#### `__init__(adapter, evaluation_engine, llm_client, artifact_manager=None, config=None)`

Initialize evolution engine.

#### `evolve(evaluation_results, reflection, behavior_names=None, context=None) -> Dict`

Evolve agent prompts using GEPA optimization.

**Parameters:**
- `evaluation_results`: Results from evaluation
- `reflection`: Reflection string from reflection engine
- `behavior_names`: Optional list of behaviors to optimize for
- `context`: Optional context dictionary

**Returns:**
- Dictionary containing evolved prompts and metadata

**Example:**
```python
from codeoptix.evolution import EvolutionEngine

engine = EvolutionEngine(adapter, eval_engine, llm_client)
evolved = engine.evolve(results, reflection, behavior_names=["insecure-code"])
```

---

## Artifact Manager

### `ArtifactManager`

Manages evaluation artifacts.

#### `save_results(results, run_id=None) -> Path`

Save evaluation results to JSON file.

**Parameters:**
- `results`: Results dictionary to save
- `run_id`: Optional run ID (generated if not provided)

**Returns:**
- Path to saved results file

#### `load_results(run_id) -> Dict`

Load evaluation results from file.

**Parameters:**
- `run_id`: Run ID to load

**Returns:**
- Results dictionary

#### `save_reflection(reflection_content, run_id=None) -> Path`

Save reflection report to markdown file.

**Parameters:**
- `reflection_content`: Reflection markdown content
- `run_id`: Optional run ID (generated if not provided)

**Returns:**
- Path to saved reflection file

#### `save_evolved_prompts(evolved_prompts, run_id=None) -> Path`

Save evolved prompts to YAML file.

**Parameters:**
- `evolved_prompts`: Evolved prompts dictionary
- `run_id`: Optional run ID (generated if not provided)

**Returns:**
- Path to saved prompts file

#### `list_runs() -> List[Dict]`

List all evaluation runs with metadata.

**Returns:**
- List of dictionaries with run information (run_id, timestamp, score, behaviors)

---

## LLM Client

### `create_llm_client(provider, api_key=None, config=None) -> LLMClient`

Create an LLM client for the specified provider.

**Parameters:**
- `provider`: `LLMProvider.OPENAI`, `LLMProvider.ANTHROPIC`, `LLMProvider.GOOGLE`, or `LLMProvider.OLLAMA`
- `api_key`: Optional API key (required for cloud providers, not needed for Ollama)
- `config`: Optional configuration dictionary

**Returns:**
- Configured LLMClient instance

**Example:**
```python
from codeoptix.utils.llm import create_llm_client, LLMProvider

# For OpenAI
client = create_llm_client(LLMProvider.OPENAI, api_key="sk-...")
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-5.2"
)

# For Ollama (no API key needed)
ollama_client = create_llm_client(LLMProvider.OLLAMA)
```

### `LLMProvider`

Enum for supported LLM providers.

**Values:**
- `OPENAI`: OpenAI models (GPT-4, GPT-3.5)
- `ANTHROPIC`: Anthropic models (Claude)
- `GOOGLE`: Google models (Gemini)
- `OLLAMA`: Local Ollama models

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

## ACP (Agent Client Protocol) Integration

CodeOptiX supports ACP for editor integration and multi-agent workflows.

### `ACPAgentRegistry`

Registry for managing ACP-compatible agents.

#### `register(name, command, cwd=None, description=None)`

Register a new ACP agent.

#### `unregister(name)`

Remove an ACP agent from registry.

#### `list_agents() -> Dict`

List all registered agents.

#### `get_agent(name) -> Dict`

Get agent configuration by name.

### `ACPQualityBridge`

Quality bridge for ACP workflows.

#### `__init__(agent_command, behaviors=None, auto_eval=True)`

Initialize quality bridge.

**Parameters:**
- `agent_command`: Command to spawn ACP agent
- `behaviors`: Comma-separated behavior names
- `auto_eval`: Whether to auto-evaluate code quality

### `CodeOptiXAgent`

ACP agent implementation for CodeOptiX.

#### `generate_code(prompt, **kwargs) -> AgentOutput`

Generate code using registered adapters.

---

For usage examples, see the [Python API Guide](../guides/python-api.md).

