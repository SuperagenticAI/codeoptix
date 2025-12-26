# Error Handling

CodeOptiX includes robust error handling with retry logic and graceful degradation.

---

## Retry Logic

CodeOptiX automatically retries failed API calls with exponential backoff.

### Automatic Retries

LLM calls are automatically retried on failure:

```python
from codeoptix.utils.llm import create_llm_client

client = create_llm_client(LLMProvider.OPENAI)
# Automatically retries on failure
response = client.chat_completion(...)
```

### Custom Retry Logic

Use retry decorators for custom logic:

```python
from codeoptix.utils.retry import retry_llm_call

@retry_llm_call(max_attempts=3, initial_wait=1.0, max_wait=60.0)
def my_api_call():
    # Your API call
    pass
```

---

## Error Types

### APIError

General API errors:

```python
from codeoptix.utils.retry import APIError

try:
    result = llm_client.chat_completion(...)
except APIError as e:
    print(f"API error: {e}")
```

### RateLimitError

Rate limit errors:

```python
from codeoptix.utils.retry import RateLimitError

try:
    result = llm_client.chat_completion(...)
except RateLimitError as e:
    print("Rate limit exceeded. Please wait.")
```

### TimeoutError

Timeout errors:

```python
from codeoptix.utils.retry import TimeoutError

try:
    result = llm_client.chat_completion(...)
except TimeoutError as e:
    print("Request timed out. Try again.")
```

---

## User-Friendly Error Messages

### Generate Error Messages

```python
from codeoptix.utils.retry import handle_api_error

try:
    result = llm_client.chat_completion(...)
except Exception as e:
    message = handle_api_error(e, context="LLM call")
    print(message)
```

### Error Message Examples

- **Rate limit**: "Rate limit exceeded. Please wait before retrying."
- **Timeout**: "Request timed out. The service may be slow. Try again."
- **Authentication**: "Authentication failed. Please check your API key."
- **Quota**: "API quota exceeded. Please check your account limits."

---

## Graceful Degradation

### Fallback Scenarios

If scenario generation fails, CodeOptiX uses fallback scenarios:

```python
# Automatic fallback
scenarios = generator.generate_scenarios(...)
# Falls back to simple scenarios on error
```

### Fallback Evaluation

If evaluation fails, CodeOptiX continues with other scenarios:

```python
# Continues with other scenarios
results = engine.evaluate_behaviors(...)
```

---

## Best Practices

### 1. Handle Errors Explicitly

Always handle errors in your code:

```python
try:
    results = engine.evaluate_behaviors(...)
except Exception as e:
    print(f"Evaluation failed: {e}")
    # Handle error
```

### 2. Use Retry Logic

Use retry logic for transient errors:

```python
@retry_llm_call(max_attempts=3)
def critical_call():
    # Your critical API call
    pass
```

### 3. Check Results

Always check if results are valid:

```python
results = engine.evaluate_behaviors(...)
if not results or "behaviors" not in results:
    print("Evaluation failed")
```

---

## Configuration

### Retry Configuration

```python
config = {
    "retry": {
        "max_attempts": 3,
        "initial_wait": 1.0,
        "max_wait": 60.0
    }
}
```

---

## Troubleshooting

### Too Many Retries

Reduce retry attempts:

```python
@retry_llm_call(max_attempts=2)  # Reduce attempts
def call():
    pass
```

### Slow Responses

Increase timeout:

```python
config = {
    "timeout": 120  # Increase timeout
}
```

---

## Next Steps

- [Python API Guide](../guides/python-api.md) - Error handling in Python
- [CLI Usage Guide](../guides/cli-usage.md) - CLI error handling
- [Configuration Guide](../guides/configuration.md) - Error handling configuration

