# CodeOptiX API Documentation

## Overview

CodeOptiX provides a comprehensive API for behavioral optimization of coding agents. This document covers the main components and their usage.

## Core Components

### Agent Adapters

#### `create_adapter(adapter_type: str, config: Dict[str, Any]) -> AgentAdapter`

Create an agent adapter for a specific agent type.

**Parameters:**
- `adapter_type`: One of `"claude-code"`, `"codex"`, `"gemini-cli"`
- `config`: Configuration dictionary with `llm_config` and optional `prompt`

**Returns:**
- `AgentAdapter` instance

**Example:**
```python
from codeoptix.adapters.factory import create_adapter

config = {
    "llm_config": {
        "provider": "anthropic",
        "api_key": "your-api-key",
        "model": "claude-sonnet-4.5"
    },
    "prompt": "You are a helpful coding assistant."
}

adapter = create_adapter("claude-code", config)
```

### Evaluation Engine

#### `EvaluationEngine`

Main orchestrator for behavioral evaluation.

**Initialization:**
```python
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

llm_client = create_llm_client(LLMProvider.OPENAI, api_key="...")
engine = EvaluationEngine(adapter, llm_client, config={
    "scenario_generator": {
        "num_scenarios": 3,
        "use_bloom": True
    }
})
```

**Methods:**

- `evaluate_behaviors(behavior_names: List[str], scenarios: Optional[List[Dict]] = None, context: Optional[Dict] = None) -> Dict[str, Any]`

  Evaluate agent against behavior specifications.

  **Parameters:**
  - `behavior_names`: List of behavior names to evaluate
  - `scenarios`: Optional pre-generated scenarios
  - `context`: Optional context (plan, requirements, etc.)

  **Returns:**
  - Dictionary with evaluation results including:
    - `behaviors`: Dict of behavior evaluation results
    - `overall_score`: Float between 0.0 and 1.0
    - `scenarios`: List of scenarios used
    - `metadata`: Additional metadata

### Behavior Specifications

#### `create_behavior(name: str, config: Optional[Dict] = None) -> BehaviorSpec`

Create a behavior specification.

**Available Behaviors:**
- `"insecure-code"`: Detects security vulnerabilities
- `"vacuous-tests"`: Identifies low-quality tests
- `"plan-drift"`: Detects deviations from plans

**Example:**
```python
from codeoptix.behaviors import create_behavior

behavior = create_behavior("insecure-code", config={
    "severity": "high",
    "enabled": True
})

result = behavior.evaluate(agent_output, context={})
```

### Reflection Engine

#### `ReflectionEngine`

Generates reflection reports from evaluation results.

**Initialization:**
```python
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager

artifact_manager = ArtifactManager()
engine = ReflectionEngine(artifact_manager)
```

**Methods:**

- `reflect(results: Dict[str, Any], agent_name: Optional[str] = None, save: bool = True) -> str`

  Generate reflection from evaluation results.

  **Returns:**
  - Markdown string with reflection content

- `reflect_from_run_id(run_id: str, agent_name: Optional[str] = None) -> str`

  Generate reflection from a previous evaluation run.

### Evolution Engine

#### `EvolutionEngine`

Optimizes agent prompts using GEPA-style evolution.

**Initialization:**
```python
from codeoptix.evolution import EvolutionEngine

evolution_engine = EvolutionEngine(
    adapter=adapter,
    evaluation_engine=eval_engine,
    llm_client=llm_client,
    artifact_manager=artifact_manager,
    config={
        "max_iterations": 3,
        "population_size": 3,
        "minibatch_size": 2
    }
)
```

**Methods:**

- `evolve(evaluation_results: Dict[str, Any], reflection: str, behavior_names: Optional[List[str]] = None, context: Optional[Dict] = None) -> Dict[str, Any]`

  Evolve agent prompts based on evaluation results.

  **Returns:**
  - Dictionary with evolved prompts and metadata

### Artifact Manager

#### `ArtifactManager`

Manages storage and retrieval of evaluation artifacts.

**Methods:**

- `save_results(results: Dict[str, Any], run_id: Optional[str] = None) -> Path`
- `load_results(run_id: str) -> Dict[str, Any]`
- `save_reflection(reflection_content: str, run_id: Optional[str] = None) -> Path`
- `load_reflection(run_id: str) -> str`
- `save_evolved_prompts(evolved_prompts: Dict[str, Any], run_id: Optional[str] = None) -> Path`
- `load_evolved_prompts(run_id: str) -> Dict[str, Any]`
- `list_runs() -> List[Dict[str, Any]]`

### LLM Client

#### `create_llm_client(provider: LLMProvider, api_key: Optional[str] = None) -> LLMClient`

Create an LLM client for a specific provider.

**Providers:**
- `LLMProvider.ANTHROPIC`
- `LLMProvider.OPENAI`
- `LLMProvider.GOOGLE`

**Example:**
```python
from codeoptix.utils.llm import create_llm_client, LLMProvider

client = create_llm_client(LLMProvider.OPENAI, api_key="...")
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o"
)
```

## Error Handling

CodeOptiX includes robust error handling with retry logic:

```python
from codeoptix.utils.retry import retry_llm_call, APIError, RateLimitError

@retry_llm_call(max_attempts=3)
def call_api():
    # Your API call here
    pass
```

## Configuration

CodeOptiX can be configured via YAML or JSON:

```yaml
adapter:
  llm_config:
    provider: openai
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}

evaluation:
  scenario_generator:
    num_scenarios: 3
    use_bloom: true
    use_full_bloom: true
  static_analysis:
    bandit: true

evolution:
  max_iterations: 3
  population_size: 3
  proposer:
    use_gepa: true
```

## Examples

See the `examples/` directory for complete examples:
- `behavioral_spec_example.py` - Full pipeline example
- `gepa_demonstration.py` - GEPA integration demo
- `basic_adapter_usage.py` - Adapter usage

## Testing

Run tests with:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src/codeoptix --cov-report=html
```

