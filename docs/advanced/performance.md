# Performance Guide

Optimizing CodeOptiX performance for different use cases.

---

## Performance Optimization Strategies

### For Local Development

**Use Ollama for fastest evaluation:**

```bash
# Install Ollama and pull a model
ollama pull llama3.2

# Run evaluation (no API key needed)
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider ollama
```

**Benefits:**
- ✅ No API rate limits
- ✅ No network latency
- ✅ No API costs
- ✅ Runs entirely locally

### For CI/CD Pipelines

**Use the `ci` command optimized for automation:**

```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --fail-on-failure \
  --output-format summary
```

**Configuration for CI:**
```yaml
evaluation:
  scenario_generator:
    num_scenarios: 2  # Reduce from default 5
    use_bloom: false  # Disable complex scenario generation

evolution:
  max_iterations: 1   # Reduce evolution iterations
```

### For Production Evaluation

**Use cloud providers with optimized settings:**

```yaml
adapter:
  llm_config:
    provider: anthropic
    model: claude-opus-4-5-20251101  # Latest Opus model
    temperature: 0.1  # Lower temperature for consistency

evaluation:
  scenario_generator:
    num_scenarios: 3
    use_bloom: true

  static_analysis:
    bandit: true
    safety: true
    # Disable slower linters
    pylint: false
    mypy: false
```

---

## Benchmarking Performance

### Run Performance Tests

```bash
# Time a full evaluation
time codeoptix eval \
  --agent codex \
  --behaviors "insecure-code,vacuous-tests" \
  --llm-provider openai
```

### Profile Memory Usage

```bash
# Monitor memory during evaluation
codeoptix eval --agent codex --behaviors insecure-code &
pid=$!
while kill -0 $pid 2>/dev/null; do
    ps -o pid,ppid,cmd,%mem,%cpu -p $pid
    sleep 1
done
```

### Compare Different Configurations

```bash
# Test with different providers
for provider in openai anthropic google ollama; do
    echo "Testing $provider..."
    time codeoptix eval --agent codex --behaviors insecure-code --llm-provider $provider
done
```

---

## Performance by Component

### LLM Providers (API Response Time)

| Provider | Model | Avg Response Time | Cost |
|----------|-------|-------------------|------|
| Ollama | llama3.2 | 2-5s | Free |
| Anthropic | claude-opus-4-5 | 3-8s | $$$ |
| OpenAI | gpt-5.2 | 2-6s | $$$ |
| Google | gemini-3-pro | 4-10s | $$ |

### Behaviors (Evaluation Time)

| Behavior | Complexity | Avg Time |
|----------|------------|----------|
| insecure-code | Medium | 10-30s |
| vacuous-tests | Low | 5-15s |
| plan-drift | High | 20-60s |

### Scenario Generation

- **Without Bloom**: 5-15s per scenario
- **With Bloom**: 30-90s per scenario
- **Recommendation**: Use Bloom only when needed for complex behaviors

---

## Memory Optimization

### Large Codebases

For evaluating large codebases:

```yaml
evaluation:
  static_analysis:
    # Enable memory-efficient linters
    bandit: true
    safety: true
    ruff: true

    # Disable memory-intensive linters
    pylint: false
    mypy: false

linters:
  # Limit concurrent linters
  max_concurrent: 2
```

### Resource Constraints

For systems with limited resources:

```bash
# Use smaller Ollama models
ollama pull llama3.2:1b  # 1B parameter model

# Limit evaluation scope
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --config minimal-config.yaml
```

---

## Caching and Reuse

### Reuse Evaluation Results

```bash
# Save results for reuse
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --output results.json

# Generate reflection from saved results
codeoptix reflect --input results.json

# Evolve from saved results
codeoptix evolve --input results.json
```

### Cache LLM Responses

For repeated evaluations of similar code:

```python
# Implement caching in custom adapter
from functools import lru_cache

class CachedLLMClient:
    def __init__(self, client):
        self.client = client

    @lru_cache(maxsize=100)
    def chat_completion(self, messages, model, **kwargs):
        # Cache based on prompt content
        prompt_hash = hash(str(messages))
        return self.client.chat_completion(messages, model, **kwargs)
```

---

## Scaling Considerations

### Multiple Agents

Evaluate multiple agents in parallel:

```bash
# Run evaluations in background
for agent in claude-code codex gemini-cli; do
    codeoptix eval --agent $agent --behaviors insecure-code &
done
wait
```

### Batch Processing

Process multiple evaluation requests:

```python
from codeoptix.evaluation import EvaluationEngine
from concurrent.futures import ThreadPoolExecutor

def evaluate_batch(requests):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(evaluate_single, req)
            for req in requests
        ]
        return [f.result() for f in futures]
```

---

## Monitoring and Alerting

### Set Up Monitoring

```bash
# Monitor evaluation performance
codeoptix eval --agent codex --behaviors insecure-code 2>&1 | tee eval.log

# Check for errors
if grep -q "ERROR\|FAILED" eval.log; then
    echo "Evaluation failed"
    exit 1
fi
```

### Performance Alerts

```bash
# Alert if evaluation takes too long
timeout 300 codeoptix eval --agent codex --behaviors insecure-code

if [ $? -eq 124 ]; then
    echo "Evaluation timed out after 5 minutes"
    # Send alert
fi
```

---

## Best Practices

### Development Workflow

1. **Local Development**: Use Ollama for fast iteration
2. **Pre-commit**: Use `codeoptix lint` for quick checks
3. **CI/CD**: Use `codeoptix ci` for automated quality gates
4. **Production**: Use cloud providers with optimized configs

### Configuration Templates

**Fast Development:**
```yaml
evaluation:
  scenario_generator:
    num_scenarios: 1
    use_bloom: false

llm:
  provider: ollama
  model: llama3.2
```

**Production Quality:**
```yaml
evaluation:
  scenario_generator:
    num_scenarios: 5
    use_bloom: true

  static_analysis:
    bandit: true
    safety: true
    ruff: true

llm:
  provider: anthropic
  model: claude-opus-4-5-20251101
```

**CI/CD Optimized:**
```yaml
evaluation:
  scenario_generator:
    num_scenarios: 2
    use_bloom: false

output:
  format: summary

behavior:
  fail_on_failure: true
```