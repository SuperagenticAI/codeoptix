# Custom Behaviors Guide

Learn how to create your own behavior specifications.

---

## Overview

Behavior specifications are modular, reusable rules that evaluate agent output. You can create custom behaviors for your specific needs.

---

## Creating a Custom Behavior

### Step 1: Extend BehaviorSpec

```python
from codeoptix.behaviors.base import BehaviorSpec, BehaviorResult, Severity
from codeoptix.adapters.base import AgentOutput

class MyCustomBehavior(BehaviorSpec):
    def get_name(self) -> str:
        return "my-custom-behavior"
    
    def get_description(self) -> str:
        return "Checks for specific patterns in code"
    
    def evaluate(self, agent_output: AgentOutput, context=None):
        code = agent_output.code or ""
        evidence = []
        score = 1.0
        
        # Your evaluation logic here
        if "bad_pattern" in code:
            evidence.append("Found bad pattern in code")
            score = 0.5
        
        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=score >= 0.7,
            score=score,
            evidence=evidence,
            severity=Severity.MEDIUM
        )
```

### Step 2: Register Behavior

```python
from codeoptix.behaviors import create_behavior

# Register your behavior
# (Implementation depends on your setup)

behavior = create_behavior("my-custom-behavior")
```

---

## Example: Code Style Behavior

Check for code style issues:

```python
class CodeStyleBehavior(BehaviorSpec):
    def get_name(self) -> str:
        return "code-style"
    
    def get_description(self) -> str:
        return "Checks code style and formatting"
    
    def evaluate(self, agent_output, context=None):
        code = agent_output.code or ""
        evidence = []
        score = 1.0
        
        # Check for long lines
        for i, line in enumerate(code.split('\n'), 1):
            if len(line) > 100:
                evidence.append(f"Line {i} exceeds 100 characters")
                score -= 0.1
        
        # Check for missing docstrings
        if 'def ' in code and '"""' not in code:
            evidence.append("Missing docstrings")
            score -= 0.2
        
        score = max(0.0, score)  # Ensure non-negative
        
        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=score >= 0.7,
            score=score,
            evidence=evidence,
            severity=Severity.LOW
        )
```

---

## Example: Performance Behavior

Check for performance issues:

```python
class PerformanceBehavior(BehaviorSpec):
    def get_name(self) -> str:
        return "performance"
    
    def get_description(self) -> str:
        return "Checks for performance issues"
    
    def evaluate(self, agent_output, context=None):
        code = agent_output.code or ""
        evidence = []
        score = 1.0
        
        # Check for inefficient patterns
        if "for i in range(len(" in code:
            evidence.append("Inefficient range(len()) pattern")
            score -= 0.3
        
        if ".append(" in code and "list comprehension" not in code.lower():
            # Check if list comprehension could be used
            evidence.append("Consider using list comprehension")
            score -= 0.1
        
        score = max(0.0, score)
        
        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=score >= 0.7,
            score=score,
            evidence=evidence,
            severity=Severity.MEDIUM
        )
```

---

## Using LLM Evaluation

You can use LLM for semantic evaluation:

```python
class SemanticBehavior(BehaviorSpec):
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = config.get("llm_client")
    
    def evaluate(self, agent_output, context=None):
        if not self.llm_client:
            return BehaviorResult(
                behavior_name=self.get_name(),
                passed=False,
                score=0.0,
                evidence=["LLM client not configured"]
            )
        
        # Use LLM to evaluate
        prompt = f"Evaluate this code: {agent_output.code}"
        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o"
        )
        
        # Parse response and create result
        # ...
```

---

## Configuration

Custom behaviors can accept configuration:

```python
class ConfigurableBehavior(BehaviorSpec):
    def __init__(self, config=None):
        super().__init__(config)
        self.threshold = config.get("threshold", 0.7)
        self.strict_mode = config.get("strict_mode", False)
    
    def evaluate(self, agent_output, context=None):
        # Use configuration
        score = self._calculate_score(agent_output)
        passed = score >= self.threshold
        
        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=passed,
            score=score,
            evidence=[],
            severity=Severity.MEDIUM
        )
```

---

## Best Practices

### 1. Clear Evidence

Provide specific, actionable evidence:

```python
evidence.append(f"Hardcoded password found at line {line_num}: {match.group(0)}")
```

### 2. Appropriate Scoring

Use consistent scoring:
- 1.0 = Perfect
- 0.7-0.9 = Good
- 0.5-0.7 = Fair
- 0.0-0.5 = Poor

### 3. Handle Edge Cases

Always handle missing or empty code:

```python
code = agent_output.code or ""
if not code:
    return BehaviorResult(
        behavior_name=self.get_name(),
        passed=False,
        score=0.0,
        evidence=["No code provided"]
    )
```

---

## Testing Custom Behaviors

Test your custom behavior:

```python
def test_my_behavior():
    behavior = MyCustomBehavior()
    output = AgentOutput(code="bad_pattern here")
    result = behavior.evaluate(output)
    
    assert not result.passed
    assert len(result.evidence) > 0
```

---

## Next Steps

- [Behavior Specifications](../concepts/behaviors.md) - Learn about behaviors
- [Evaluation Engine](../concepts/evaluation.md) - Use behaviors in evaluation
- [Python API Guide](python-api.md) - Advanced usage

