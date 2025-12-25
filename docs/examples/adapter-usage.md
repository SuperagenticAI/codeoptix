# Adapter Usage Examples

Examples of using different agent adapters.

---

## Codex Adapter

### Basic Usage

```python
from codeoptix.adapters.factory import create_adapter

adapter = create_adapter("codex", {
    "llm_config": {
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-5.2"
    }
})

output = adapter.execute("Write a Python function to calculate factorial")
print(output.code)
```

---

## Claude Code Adapter

### Basic Usage

```python
adapter = create_adapter("claude-code", {
    "llm_config": {
        "provider": "anthropic",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-sonnet-4.5"
    }
})

output = adapter.execute("Write secure authentication code")
print(output.code)
```

---

## Gemini CLI Adapter

### Basic Usage

```python
adapter = create_adapter("gemini-cli", {
    "llm_config": {
        "provider": "google",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "model": "gemini-3-flash"
    }
})

output = adapter.execute("Write a REST API endpoint")
print(output.code)
```

---

## Updating Prompts

### Update System Prompt

```python
adapter.update_prompt(
    "You are a security-focused coding assistant. "
    "Never include hardcoded secrets in code."
)

current_prompt = adapter.get_prompt()
print(current_prompt)
```

---

## With Context

### Provide Context

```python
output = adapter.execute(
    "Create a database connection function",
    context={
        "requirements": [
            "Use environment variables for credentials",
            "Include error handling",
            "Add connection pooling"
        ],
        "plan": "Secure database access implementation"
    }
)
```

---

## Next Steps

- [Agent Adapters](../concepts/adapters.md) - Learn about adapters
- [Python API Guide](../guides/python-api.md) - More examples
- [Behavioral Spec Example](behavioral-spec.md) - Complete example

