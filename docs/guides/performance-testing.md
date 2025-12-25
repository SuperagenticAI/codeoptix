# Performance Testing Guide

!!! warning "Planned Feature"
    **Performance testing is currently a planned feature, not yet implemented.**
    
    This guide shows how you can implement performance testing yourself by creating custom behaviors.
    The dependency (`locust`) is available as an optional dependency,
    but you'll need to implement the evaluators yourself.

---

## Installation

Install performance testing dependencies:

```bash
pip install codeoptix[performance]
```

This installs:
- `locust` - Load testing framework

---

## Use Cases

Performance testing in CodeOptiX would be useful for:

- ✅ **Load testing** web applications
- ✅ **Stress testing** APIs and endpoints
- ✅ **Performance benchmarking** of agent-generated code
- ✅ **Identifying bottlenecks** in applications
- ✅ **Validating performance requirements**

---

## Implementation Guide

!!! note "Custom Implementation Required"
    Since performance testing is not yet implemented in CodeOptiX, you'll need to create your own
    custom behavior and evaluator. Here's how:

### 1. Create a Performance Test Behavior

Create a custom behavior that uses performance testing:

```python
from codeoptix.behaviors.base import BehaviorSpec
from codeoptix.evaluation.evaluators import LLMEvaluator

class PerformanceBehavior(BehaviorSpec):
    """Test application performance."""
    
    def get_name(self) -> str:
        return "performance"
    
    def get_description(self) -> str:
        return "Validates application performance under load"
    
    def create_evaluator(self):
        # For now, use LLMEvaluator or create your own
        # TODO: Implement PerformanceEvaluator
        return None  # You'll need to implement this
```

### 2. Implement Performance Test Evaluator (Example)

!!! note "Example Implementation"
    This is an example of how you could implement performance testing. You'll need to integrate
    this into CodeOptiX's evaluation system yourself.

```python
# Example: Custom Performance Test Evaluator
# This is NOT part of CodeOptiX yet - you need to implement this yourself

from locust import HttpUser, task, between
from locust.env import Environment
import gevent
from typing import Dict, Any

class PerformanceEvaluator:
    """Example: Evaluates performance using Locust."""
    
    def evaluate(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run performance tests."""
        url = context.get("url", "http://localhost:8000")
        users = context.get("users", 10)
        spawn_rate = context.get("spawn_rate", 2)
        run_time = context.get("run_time", "30s")
        
        # Define user behavior
        class WebsiteUser(HttpUser):
            wait_time = between(1, 3)
            host = url
            
            @task
            def index(self):
                self.client.get("/")
            
            @task(3)
            def api_endpoint(self):
                self.client.get("/api/data")
        
        # Setup Locust environment
        env = Environment(user_classes=[WebsiteUser])
        env.create_local_runner()
        
        # Start test
        env.runner.start(users, spawn_rate=spawn_rate)
        
        # Run for specified duration
        gevent.spawn_later(int(run_time.rstrip('s')), lambda: env.runner.quit())
        
        # Wait for test to complete
        env.runner.greenlet.join()
        
        # Get statistics
        stats = env.stats
        
        issues = []
        score = 1.0
        
        # Check response times
        for name, entry in stats.entries.items():
            if entry.num_requests > 0:
                avg_response_time = entry.avg_response_time
                max_response_time = entry.max_response_time
                
                # Check if response times are acceptable
                if avg_response_time > 1000:  # 1 second
                    issues.append(f"{name}: Average response time too high ({avg_response_time:.0f}ms)")
                    score -= 0.2
                
                if max_response_time > 5000:  # 5 seconds
                    issues.append(f"{name}: Max response time too high ({max_response_time:.0f}ms)")
                    score -= 0.1
                
                # Check failure rate
                failure_rate = entry.num_failures / entry.num_requests if entry.num_requests > 0 else 0
                if failure_rate > 0.01:  # 1% failure rate
                    issues.append(f"{name}: Failure rate too high ({failure_rate:.1%})")
                    score -= 0.3
        
        # Check total requests
        total_requests = sum(entry.num_requests for entry in stats.entries.values())
        if total_requests < 100:
            issues.append(f"Too few requests completed: {total_requests}")
            score -= 0.1
        
        score = max(0.0, score)
        
        return {
            "passed": len(issues) == 0,
            "score": score,
            "evidence": issues,
            "stats": {
                "total_requests": total_requests,
                "total_failures": sum(entry.num_failures for entry in stats.entries.values()),
            }
        }
```

---

## Configuration

### Basic Configuration

```python
context = {
    "url": "http://localhost:8000",
    "users": 10,           # Number of concurrent users
    "spawn_rate": 2,       # Users spawned per second
    "run_time": "30s",     # Test duration
}
```

### Advanced Configuration

```python
context = {
    "url": "http://localhost:8000",
    "users": 50,           # Higher load
    "spawn_rate": 5,       # Faster ramp-up
    "run_time": "2m",      # Longer test
    "max_response_time": 500,  # Custom threshold (ms)
    "max_failure_rate": 0.01,  # 1% max failures
}
```

---

## Example: API Performance Test

```python
from codeoptix.behaviors.base import BehaviorSpec
from codeoptix.evaluation.evaluators import BaseEvaluator
from locust import HttpUser, task, between
from locust.env import Environment
import gevent

class APIPerformanceBehavior(BehaviorSpec):
    """Tests API performance."""
    
    def get_name(self) -> str:
        return "api-performance"
    
    def get_description(self) -> str:
        return "Validates API performance under load"
    
    def create_evaluator(self) -> BaseEvaluator:
        return APIPerformanceEvaluator()

class APIPerformanceEvaluator(BaseEvaluator):
    def evaluate(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        url = context.get("url", "http://localhost:8000")
        users = context.get("users", 20)
        
        class APIUser(HttpUser):
            wait_time = between(0.5, 2)
            host = url
            
            @task(5)
            def get_users(self):
                self.client.get("/api/users")
            
            @task(3)
            def get_posts(self):
                self.client.get("/api/posts")
            
            @task(1)
            def create_post(self):
                self.client.post("/api/posts", json={
                    "title": "Test",
                    "content": "Test content"
                })
        
        env = Environment(user_classes=[APIUser])
        env.create_local_runner()
        
        # Run test
        env.runner.start(users, spawn_rate=2)
        gevent.spawn_later(30, lambda: env.runner.quit())
        env.runner.greenlet.join()
        
        # Analyze results
        issues = []
        stats = env.stats
        
        for name, entry in stats.entries.items():
            if entry.num_requests > 0:
                avg_time = entry.avg_response_time
                p95_time = entry.get_response_time_percentile(0.95)
                
                if avg_time > 500:
                    issues.append(f"{name}: Avg {avg_time:.0f}ms (target: <500ms)")
                
                if p95_time > 1000:
                    issues.append(f"{name}: P95 {p95_time:.0f}ms (target: <1000ms)")
        
        score = 1.0 if len(issues) == 0 else max(0.0, 1.0 - len(issues) * 0.15)
        
        return {
            "passed": len(issues) == 0,
            "score": score,
            "evidence": issues,
        }
```

---

## Running Performance Tests

### With CodeOptiX CLI

```bash
# Set up your application URL
export APP_URL="http://localhost:8000"

# Run performance evaluation
codeoptix eval \
  --agent codex \
  --behaviors api-performance \
  --context '{"url": "http://localhost:8000", "users": 20, "run_time": "30s"}' \
  --llm-provider openai
```

### With Python API

```python
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider
import os

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

# Run performance test
results = engine.evaluate_behaviors(
    behavior_names=["api-performance"],
    context={
        "url": "http://localhost:8000",
        "users": 20,
        "spawn_rate": 2,
        "run_time": "30s",
    }
)

print(f"Performance Score: {results['overall_score']:.2%}")
```

---

## Standalone Locust Tests

You can also run Locust tests directly:

### Create `locustfile.py`

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"
    
    @task
    def index(self):
        self.client.get("/")
    
    @task(3)
    def api(self):
        self.client.get("/api/data")
```

### Run Locust

```bash
# Web UI mode
locust

# Headless mode
locust --headless -u 10 -r 2 -t 30s
```

---

## Best Practices

### 1. Start Small

Begin with low user counts and gradually increase:

```python
context = {
    "users": 5,      # Start small
    "spawn_rate": 1,
    "run_time": "10s",
}
```

### 2. Set Realistic Targets

Define performance thresholds:

```python
max_response_time = 500  # 500ms
max_failure_rate = 0.01  # 1%
```

### 3. Monitor Resources

Watch server resources during tests:

```bash
# Monitor CPU and memory
top
htop
```

### 4. Use Ramp-Up

Gradually increase load:

```python
context = {
    "spawn_rate": 2,  # 2 users per second
}
```

### 5. Test Different Scenarios

Test various endpoints and user behaviors:

```python
@task(5)
def light_endpoint(self):
    self.client.get("/api/status")

@task(1)
def heavy_endpoint(self):
    self.client.get("/api/complex-query")
```

---

## Troubleshooting

### Locust Not Found

```bash
pip install codeoptix[performance]
```

### Tests Too Slow

Reduce user count or test duration:

```python
context = {
    "users": 5,        # Lower users
    "run_time": "10s", # Shorter duration
}
```

### Connection Errors

Check if the application is running:

```bash
curl http://localhost:8000
```

### Memory Issues

Reduce concurrent users:

```python
context = {
    "users": 10,  # Lower concurrent users
}
```

---

## Next Steps

- [Custom Behaviors Guide](custom-behaviors.md) - Create your own performance behaviors
- [Python API Guide](python-api.md) - Advanced usage
- [Configuration Guide](configuration.md) - Configure performance testing

---

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [CodeOptiX Behaviors](../concepts/behaviors.md)
- [Performance Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)

