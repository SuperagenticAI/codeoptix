# Agent Adapters

Agent adapters connect CodeOptiX to your coding agent, allowing CodeOptiX to execute tasks and evaluate behavior.

---

## What are Adapters?

Adapters are **interfaces** that translate between CodeOptiX's standard format and your agent's specific API. They allow CodeOptiX to work with any coding agent.

---

## Supported Adapters

### Codex (OpenAI GPT-4)

OpenAI's GPT-4 Code Interpreter.

```python
adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o"
    }
})
```

### Claude Code (Anthropic)

Anthropic's Claude for coding.

```python
adapter = create_adapter("claude-code", {
    "llm_config": {
        "provider": "anthropic",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-sonnet-4.5"
    }
})
```

### Gemini CLI (Google)

Google's Gemini for coding.

```python
adapter = create_adapter("gemini-cli", {
    "llm_config": {
        "provider": "google",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "model": "gemini-3-flash"
    }
})
```

---

## Adapter Interface

All adapters implement the same interface:

### `execute(prompt, context=None) -> AgentOutput`

Execute a task and return standardized output.

**Parameters:**
- `prompt`: Task description
- `context`: Optional context (files, workspace info)

**Returns:**
- `AgentOutput` with code, tests, and metadata

### `get_prompt() -> str`

Get the current agent prompt.

### `update_prompt(new_prompt) -> None`

Update the agent's system prompt.

### `get_adapter_type() -> str`

Get the adapter type identifier.

---

## Creating an Adapter

### Using the Factory

```python
from codeoptix.adapters.factory import create_adapter

adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": "sk-...",
    },
    "prompt": "You are a helpful coding assistant."
})
```

### Configuration

Adapters accept a configuration dictionary:

```python
config = {
    "llm_config": {
        "provider": "openai",  # or "anthropic", "google"
        "api_key": "sk-...",
        "model": "gpt-4o"  # Optional, has defaults
    },
    "prompt": "Custom system prompt"  # Optional
}
```

---

## Using Adapters

### Execute a Task

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
# Get current prompt
current = adapter.get_prompt()

# Update prompt
adapter.update_prompt("You are a security-focused coding assistant.")
```

---

## AgentOutput Structure

The `AgentOutput` dataclass contains:

```python
@dataclass
class AgentOutput:
    code: str                    # Generated code
    tests: Optional[str] = None  # Generated tests
    traces: Optional[List] = None  # Execution traces
    metadata: Optional[Dict] = None  # Additional metadata
    prompt_used: Optional[str] = None  # Prompt that was used
```

---

## Custom Adapters

You can create custom adapters by implementing the `AgentAdapter` interface:

```python
from codeoptix.adapters.base import AgentAdapter, AgentOutput

class MyCustomAdapter(AgentAdapter):
    def execute(self, prompt: str, context=None):
        # Your implementation
        return AgentOutput(code="...", tests="...")
    
    def get_prompt(self) -> str:
        return self._current_prompt
    
    def update_prompt(self, new_prompt: str):
        self._current_prompt = new_prompt
    
    def get_adapter_type(self) -> str:
        return "my-custom-adapter"
```

---

## Best Practices

### 1. Use Environment Variables

Always use environment variables for API keys:

```python
import os

adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
})
```

### 2. Set Appropriate Prompts

Set clear, specific prompts:

```python
adapter.update_prompt(
    "You are a security-focused coding assistant. "
    "Never include hardcoded secrets in code."
)
```

### 3. Provide Context

Use context for better results:

```python
output = adapter.execute(
    prompt,
    context={
        "plan": "Create secure authentication",
        "requirements": ["No hardcoded secrets", "Use environment variables"]
    }
)
```

---

## Troubleshooting

### Adapter Not Found

Make sure you're using a supported adapter type:
- `codex`
- `claude-code`
- `gemini-cli`

### API Key Errors

Verify your API key is set correctly:

```python
import os
print(os.getenv("OPENAI_API_KEY"))  # Should not be None
```

### Execution Errors

Check that your agent is properly configured and the API is accessible.

---

## Next Steps

- [Behavior Specifications](behaviors.md) - Define behaviors to evaluate
- [Evaluation Engine](evaluation.md) - Run evaluations
- [Python API Guide](../guides/python-api.md) - Advanced usage

