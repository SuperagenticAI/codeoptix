# Python API Guide

Complete guide to using CodeOptiX in Python.

---

## Installation

```bash
pip install codeoptix
```

---

## Quick Start

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

# Create adapter
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})

# Create evaluation engine
llm_client = create_llm_client(LLMProvider.OPENAI)
engine = EvaluationEngine(adapter, llm_client)

# Evaluate
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code"]
)

print(f"Score: {results['overall_score']:.2f}")
```

---

## Agent Adapters

### Create an Adapter

```python
from codeoptix.adapters.factory import create_adapter

adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-5.2"
    },
    "prompt": "You are a helpful coding assistant."
})
```

### Execute Tasks

```python
output = adapter.execute(
    "Write a Python function to calculate fibonacci numbers",
    context={"requirements": ["Use recursion", "Include docstring"]}
)

print(output.code)
print(output.tests)
```

### Update Prompt

```python
adapter.update_prompt("You are a security-focused coding assistant.")
current_prompt = adapter.get_prompt()
```

---

## Evaluation Engine

### Basic Evaluation

```python
from codeoptix.evaluation import EvaluationEngine

engine = EvaluationEngine(adapter, llm_client)

results = engine.evaluate_behaviors(
    behavior_names=["insecure-code", "vacuous-tests"]
)
```

### With Configuration

```python
config = {
    "scenario_generator": {
        "num_scenarios": 5,
        "use_bloom": True
    },
    "static_analysis": {
        "bandit": True
    }
}

engine = EvaluationEngine(adapter, llm_client, config=config)
```

### With Context

```python
context = {
    "plan": "Create secure authentication API",
    "requirements": ["JWT tokens", "Password hashing"]
}

results = engine.evaluate_behaviors(
    behavior_names=["plan-drift"],
    context=context
)
```

---

## Behavior Specifications

### Create Behavior

```python
from codeoptix.behaviors import create_behavior

behavior = create_behavior("insecure-code")
```

### Evaluate Output

```python
from codeoptix.adapters.base import AgentOutput

output = AgentOutput(
    code='def connect():\n    password = "secret"\n    return password',
    tests="def test_connect():\n    assert True"
)

result = behavior.evaluate(output)

print(f"Passed: {result.passed}")
print(f"Score: {result.score}")
print(f"Evidence: {result.evidence}")
```

### With Configuration

```python
behavior = create_behavior("insecure-code", {
    "severity": "high",
    "enabled": True
})
```

---

## Reflection Engine

### Generate Reflection

```python
from codeoptix.reflection import ReflectionEngine
from codeoptix.artifacts import ArtifactManager

artifact_manager = ArtifactManager()
reflection_engine = ReflectionEngine(artifact_manager)

reflection = reflection_engine.reflect(
    results=evaluation_results,
    agent_name="codex",
    save=True
)

print(reflection)
```

### From Run ID

```python
reflection = reflection_engine.reflect_from_run_id(
    run_id="abc123",
    agent_name="codex"
)
```

---

## Evolution Engine

### Evolve Prompts

```python
from codeoptix.evolution import EvolutionEngine

evolution_engine = EvolutionEngine(
    adapter=adapter,
    evaluation_engine=eval_engine,
    llm_client=llm_client,
    artifact_manager=artifact_manager
)

evolved = evolution_engine.evolve(
    evaluation_results=results,
    reflection=reflection_content,
    behavior_names=["insecure-code"]
)

print(evolved["prompts"]["system_prompt"])
```

### With Configuration

```python
config = {
    "max_iterations": 5,
    "population_size": 5,
    "proposer": {
        "use_gepa": True
    }
}

evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager, config=config
)
```

---

## Artifact Management

### Save Results

```python
from codeoptix.artifacts import ArtifactManager

artifact_manager = ArtifactManager()

results_file = artifact_manager.save_results(evaluation_results)
print(f"Saved to: {results_file}")
```

### Load Results

```python
results = artifact_manager.load_results(run_id="abc123")
```

### List Runs

```python
runs = artifact_manager.list_runs()

for run in runs:
    print(f"Run ID: {run['run_id']}")
    print(f"Score: {run['overall_score']:.2f}")
```

---

## ACP Integration

### Agent Registry

```python
from codeoptix.acp import ACPAgentRegistry

# Create registry
registry = ACPAgentRegistry()

# Register an agent
registry.register(
    name="claude-code",
    command=["python", "claude_agent.py"],
    description="Claude Code via ACP",
)

# Connect to agent
connection = await registry.connect("claude-code")
session_id = registry.get_session_id("claude-code")
```

### Quality Bridge

```python
from codeoptix.acp import ACPQualityBridge
from codeoptix.evaluation import EvaluationEngine

# Create evaluation engine
evaluation_engine = EvaluationEngine(adapter, llm_client)

# Create quality bridge
bridge = ACPQualityBridge(
    agent_name="claude-code",
    evaluation_engine=evaluation_engine,
    auto_eval=True,
    behaviors=["insecure-code", "vacuous-tests"],
    registry=registry,
)

# Connect and use
await bridge.connect()
result = await bridge.prompt("Write secure code")
```

### Multi-Agent Judge

```python
from codeoptix.acp import ACPAgentRegistry, MultiAgentJudge

# Create registry and register agents
registry = ACPAgentRegistry()
registry.register(name="claude-code", command=["python", "claude.py"])
registry.register(name="grok", command=["python", "grok.py"])

# Create multi-agent judge
judge = MultiAgentJudge(
    registry=registry,
    generate_agent="claude-code",
    judge_agent="grok",
    evaluation_engine=evaluation_engine,
)

# Generate and judge
result = await judge.generate_and_judge("Write a secure API endpoint")
print(f"Generated: {result['generated_code']}")
print(f"Judgment: {result['judgment']}")
print(f"Evaluation: {result['evaluation_results']}")
```

### Agent Orchestration

```python
from codeoptix.acp import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator(registry, evaluation_engine)

# Intelligent agent selection
# The orchestrator automatically:
# 1. Checks for preferred_agent in context
# 2. Infers task type from prompt (security, review, testing, etc.)
# 3. Matches agents with relevant capabilities
# 4. Falls back to first available agent if no match
result = await orchestrator.route_to_agent(
    prompt="Write secure Python tests",
    context={"language": "python", "preferred_agent": "claude-code"},
)

# Execute multi-agent workflow
workflow = [
    {"agent": "claude-code", "prompt": "Generate code"},
    {"agent": "grok", "prompt": "Review code"},
]
results = await orchestrator.execute_multi_agent_workflow(workflow)
```

### Code Extraction

CodeOptiX provides comprehensive code extraction from ACP messages:

```python
from codeoptix.acp.code_extractor import (
    extract_code_from_message,
    extract_all_code,
    extract_code_from_text
)

# Extract from single message
code_blocks = extract_code_from_message(acp_message)

# Extract from multiple messages
code_blocks = extract_all_code(acp_messages)

# Extract from text content
code_blocks = extract_code_from_text("```python\ndef hello():\n    pass\n```")

# Each code block contains:
# {
#     "language": "python",
#     "content": "def hello(): ...",
#     "type": "block",  # or "inline", "file_edit_new", "file_edit_old"
#     "path": "file.py"  # if from file edit
# }
```

**Supported extraction sources:**
- ✅ `AgentMessageChunk` - Agent message content
- ✅ `ToolCallStart` - Tool call initiation
- ✅ `ToolCallProgress` - Tool call progress updates
- ✅ `TextContentBlock` - Text content with code
- ✅ Raw text strings - Direct text extraction

### CodeOptiX as ACP Agent

CodeOptiX can act as an ACP agent for direct editor integration:

```python
from codeoptix.acp import CodeOptiXAgent
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client
from acp import run_agent

# Create evaluation engine and LLM client
llm_client = create_llm_client(LLMProvider.OPENAI)
evaluation_engine = EvaluationEngine(adapter, llm_client)

# Create CodeOptiX agent with quality evaluation
agent = CodeOptiXAgent(
    evaluation_engine=evaluation_engine,
    llm_client=llm_client,
    behaviors=["insecure-code", "vacuous-tests", "plan-drift"],
)

# Run as ACP agent (for editor integration)
# CodeOptiX will automatically:
# - Extract code from prompts
# - Evaluate code quality
# - Send formatted quality reports to editor
await run_agent(agent)
```

---

## Complete Example

```python
import os
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.reflection import ReflectionEngine
from codeoptix.evolution import EvolutionEngine
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
    behavior_names=["insecure-code", "vacuous-tests"]
)

artifact_manager.save_results(results)

# 3. Reflect
reflection_engine = ReflectionEngine(artifact_manager)
reflection = reflection_engine.reflect(results, save=True)

# 4. Evolve
evolution_engine = EvolutionEngine(
    adapter, eval_engine, llm_client, artifact_manager
)

evolved = evolution_engine.evolve(
    results, reflection, behavior_names=["insecure-code"]
)

# 5. Results
print(f"Initial Score: {results['overall_score']:.2f}")
print(f"Final Score: {evolved['metadata']['final_score']:.2f}")
print(f"Improvement: {evolved['metadata']['improvement']:.2f}")
```

---

## Error Handling

### Retry Logic

```python
from codeoptix.utils.retry import retry_llm_call

@retry_llm_call(max_attempts=3)
def call_api():
    # Your API call
    pass
```

### Error Messages

```python
from codeoptix.utils.retry import handle_api_error

try:
    result = llm_client.chat_completion(...)
except Exception as e:
    message = handle_api_error(e, context="LLM call")
    print(message)
```

---

## Next Steps

- [CLI Usage](cli-usage.md) - Command-line interface
- [ACP Integration Guide](acp-integration.md) - Complete ACP documentation
- [Configuration Guide](configuration.md) - Advanced configuration
- [API Reference](../api-reference.md) - Complete API reference

