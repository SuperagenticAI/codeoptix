# Behavior Specifications

Behavior specifications define what CodeOptiX evaluates. They are modular, reusable definitions of desired or undesired behaviors.

---

## What are Behavior Specifications?

Behavior specifications are **rules** that define how to evaluate agent output. They check if the agent's code exhibits specific behaviors.

---

## Built-in Behaviors

CodeOptiX includes three built-in behaviors:

### 1. insecure-code

Detects security vulnerabilities in generated code.

**What it checks:**
- Hardcoded secrets (passwords, API keys)
- SQL injection vulnerabilities
- Insecure authentication patterns
- Exposed credentials

**Example:**
```python
from codeoptix.behaviors import create_behavior

behavior = create_behavior("insecure-code")
result = behavior.evaluate(agent_output)

if not result.passed:
    print(f"Issues found: {result.evidence}")
```

### 2. vacuous-tests

Identifies low-quality or meaningless tests.

**What it checks:**
- Tests with no assertions
- Trivial tests (always pass)
- Missing edge cases
- Incomplete test coverage

**Example:**
```python
behavior = create_behavior("vacuous-tests")
result = behavior.evaluate(agent_output)

print(f"Test quality score: {result.score}")
```

### 3. plan-drift

Detects deviations from planning artifacts and requirements.

**What it checks:**
- Missing planned features
- Requirements not addressed
- API contract violations
- Architecture mismatches

**Example:**
```python
behavior = create_behavior("plan-drift")
result = behavior.evaluate(
    agent_output,
    context={
        "plan": "Create secure authentication API",
        "requirements": ["JWT tokens", "Password hashing"]
    }
)
```

---

## Behavior Result Structure

Each behavior evaluation returns a `BehaviorResult`:

```python
@dataclass
class BehaviorResult:
    behavior_name: str      # Name of the behavior
    passed: bool            # Whether it passed
    score: float            # Score from 0.0 to 1.0
    evidence: List[str]     # Specific issues found
    severity: Severity      # LOW, MEDIUM, HIGH, CRITICAL
    metadata: Dict          # Additional data
```

### Score Interpretation

- **0.9 - 1.0**: Excellent - No issues
- **0.7 - 0.9**: Good - Minor issues
- **0.5 - 0.7**: Fair - Some issues
- **0.0 - 0.5**: Poor - Significant issues

---

## Using Behaviors

### Basic Usage

```python
from codeoptix.behaviors import create_behavior
from codeoptix.adapters.base import AgentOutput

# Create behavior
behavior = create_behavior("insecure-code")

# Create agent output (example)
agent_output = AgentOutput(
    code='def connect():\n    password = "secret123"\n    return password',
    tests="def test_connect():\n    assert True"
)

# Evaluate
result = behavior.evaluate(agent_output)

# Check results
print(f"Passed: {result.passed}")
print(f"Score: {result.score}")
print(f"Evidence: {result.evidence}")
```

### With Configuration

```python
behavior = create_behavior("insecure-code", {
    "severity": "high",
    "enabled": True,
    "strict_mode": True
})
```

### With Context

```python
result = behavior.evaluate(
    agent_output,
    context={
        "plan": "Create secure API",
        "requirements": ["No hardcoded secrets", "Use environment variables"]
    }
)
```

---

## Creating Custom Behaviors

You can create custom behaviors by extending `BehaviorSpec`:

```python
from codeoptix.behaviors.base import BehaviorSpec, BehaviorResult, Severity

class MyCustomBehavior(BehaviorSpec):
    def get_name(self) -> str:
        return "my-custom-behavior"
    
    def get_description(self) -> str:
        return "Checks for specific patterns in code"
    
    def evaluate(self, agent_output, context=None):
        code = agent_output.code or ""
        evidence = []
        score = 1.0
        
        # Your evaluation logic
        if "bad_pattern" in code:
            evidence.append("Found bad pattern")
            score = 0.5
        
        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=score >= 0.7,
            score=score,
            evidence=evidence,
            severity=Severity.MEDIUM
        )
```

### Registering Custom Behaviors

```python
from codeoptix.behaviors import create_behavior

# Register your behavior
# (Implementation depends on your setup)

behavior = create_behavior("my-custom-behavior")
```

---

## Behavior Configuration

Behaviors can be configured:

```python
config = {
    "severity": "high",      # LOW, MEDIUM, HIGH, CRITICAL
    "enabled": True,         # Enable/disable behavior
    "threshold": 0.7,        # Passing threshold
    # Behavior-specific options
}
```

---

## Evaluation Process

When a behavior evaluates agent output:

1. **Extract Code**: Gets code from `AgentOutput`
2. **Run Checks**: Performs behavior-specific checks
3. **Collect Evidence**: Gathers specific issues
4. **Calculate Score**: Computes score based on findings
5. **Return Result**: Returns `BehaviorResult`

---

## Best Practices

### 1. Use Appropriate Behaviors

Choose behaviors relevant to your use case:

```python
# For security-focused projects
behaviors = ["insecure-code"]

# For test quality
behaviors = ["vacuous-tests"]

# For plan compliance
behaviors = ["plan-drift"]
```

### 2. Provide Context

Always provide context when available:

```python
result = behavior.evaluate(
    agent_output,
    context={
        "plan": plan_content,
        "requirements": requirements_list
    }
)
```

### 3. Review Evidence

Always review the evidence in results:

```python
for issue in result.evidence:
    print(f"  - {issue}")
```

---

## Combining Behaviors

You can evaluate multiple behaviors:

```python
behaviors = [
    create_behavior("insecure-code"),
    create_behavior("vacuous-tests"),
    create_behavior("plan-drift")
]

results = {}
for behavior in behaviors:
    results[behavior.get_name()] = behavior.evaluate(agent_output)
```

---

## Next Steps

- [Evaluation Engine](evaluation.md) - Run evaluations with behaviors
- [Custom Behaviors Guide](../guides/custom-behaviors.md) - Create your own
- [Python API Guide](../guides/python-api.md) - Advanced usage

