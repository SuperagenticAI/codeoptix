# ACP Integration Examples

Examples of using CodeOptiX with Agent Client Protocol (ACP).

---

## Setting Up ACP Agents

### Registering Agents

```python
from codeoptix.acp import ACPAgentRegistry

registry = ACPAgentRegistry()

# Register Claude Code agent
registry.register(
    name="claude-code",
    command="python claude_agent.py",
    description="Claude Code via ACP"
)

# Register custom agent
registry.register(
    name="my-agent",
    command="node my-agent.js",
    cwd="/path/to/agent",
    description="Custom agent implementation"
)

# List all agents
agents = registry.list_agents()
print(agents)
```

### Using Quality Bridge

```python
from codeoptix.acp import ACPQualityBridge

# Create quality bridge
bridge = ACPQualityBridge(
    agent_command="python claude_agent.py",
    behaviors="insecure-code,vacuous-tests",
    auto_eval=True
)

# The bridge will automatically evaluate code quality
# as the agent generates code
```

---

## Multi-Agent Judge Workflow

### Setting Up Multi-Agent Evaluation

```python
from codeoptix.acp import ACPAgentRegistry
from codeoptix.acp.judge import ACPJudge

registry = ACPAgentRegistry()

# Register multiple agents
registry.register("generator", "python claude_agent.py")
registry.register("judge1", "python grok_agent.py")
registry.register("judge2", "python gpt_agent.py")

# Create multi-agent judge
judge = ACPJudge(
    generate_agent="generator",
    judge_agents=["judge1", "judge2"],
    behaviors=["insecure-code", "vacuous-tests"]
)

# Run evaluation
results = await judge.evaluate_prompt(
    prompt="Write a secure user authentication system",
    context={"requirements": "Must use bcrypt, validate inputs, prevent SQL injection"}
)

print(f"Overall Score: {results['overall_score']}")
```

---

## Editor Integration

### Zed Editor Integration

1. Start CodeOptiX as ACP agent:
```bash
codeoptix acp register
```

2. Configure Zed to connect to CodeOptiX at the displayed endpoint

3. CodeOptiX will automatically evaluate code quality in real-time

### VS Code Integration

Use the ACP extension to connect to CodeOptiX agents.

---

## Custom ACP Agent Implementation

### Basic Agent Structure

```python
from acp import Agent, Server
from codeoptix.acp import CodeOptiXAgent

class MyACPAgent(Agent):
    def __init__(self):
        super().__init__()
        self.codeoptix = CodeOptiXAgent()

    async def handle_generate_code(self, prompt: str) -> dict:
        """Handle code generation requests."""
        result = await self.codeoptix.generate_code(prompt)

        return {
            "code": result.code,
            "tests": result.tests,
            "quality_score": result.metadata.get("quality_score", 0.0)
        }

# Start the agent
async def main():
    agent = MyACPAgent()
    server = Server(agent)
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## ACP Quality Bridge Example

### Automated Quality Monitoring

```python
from codeoptix.acp import ACPQualityBridge

# Bridge between editor and agent with quality checks
bridge = ACPQualityBridge(
    agent_command="python coding_agent.py",
    behaviors="insecure-code,vacuous-tests,plan-drift",
    auto_eval=True,
    quality_threshold=0.8  # Require 80% quality score
)

# The bridge will:
# 1. Forward requests to the coding agent
# 2. Evaluate generated code against behaviors
# 3. Provide quality feedback to the editor
# 4. Block low-quality code if threshold not met

await bridge.start()
```