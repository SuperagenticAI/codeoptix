# ACP (Agent Client Protocol) Integration

CodeOptiX provides comprehensive ACP integration for editor integration, multi-agent workflows, and code optimization.

## Overview

ACP (Agent Client Protocol) is a protocol for connecting AI agents to editors and other clients. CodeOptiX uses ACP to:

- **Act as an ACP agent** - Be used directly by editors (Zed, JetBrains, Neovim, VS Code)
- **Connect to other agents** - Use any ACP-compatible agent via the protocol
- **Quality bridge** - Sit between editor and agents, automatically evaluating code quality
- **Multi-agent orchestration** - Route to best agent for each task
- **Multi-agent judge** - Use different agents for generation vs. judgment

## Quick Start

### Register CodeOptiX as an ACP Agent

Make CodeOptiX available to ACP-compatible editors:

```bash
codeoptix acp register
```

This starts CodeOptiX as an ACP agent. Connect from your editor using ACP protocol.

### Use CodeOptiX as Quality Bridge

CodeOptiX can act as a quality bridge between your editor and coding agents:

```bash
# Using an agent from registry
codeoptix acp bridge --agent-name claude-code --auto-eval

# Using a direct command
codeoptix acp bridge --agent-command "python agent.py" --auto-eval
```

The quality bridge automatically:
- Extracts code from agent responses
- Evaluates code quality
- Sends feedback to your editor in real-time

### Multi-Agent Judge

Use different agents for generation and judgment:

```bash
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write a secure authentication function"
```

This will:
1. Generate code with the generate agent
2. Judge/critique the code with the judge agent
3. Evaluate both with CodeOptiX's evaluation engine

## Agent Registry

Manage ACP-compatible agents:

### Register an Agent

```bash
codeoptix acp registry add \
  --name claude-code \
  --command "python claude_agent.py" \
  --description "Claude Code via ACP" \
  --cwd /path/to/agent
```

### List Registered Agents

```bash
codeoptix acp registry list
```

### Remove an Agent

```bash
codeoptix acp registry remove --name claude-code
```

## Architecture

### Quality Bridge Mode

```
Editor (Zed, JetBrains, Neovim, VS Code)
    │
    ├─→ ACP Protocol
    │       │
    │       └─→ CodeOptiX ACP Bridge (Quality Layer)
    │               │
    │               ├─→ Quality Engineering Layer
    │               │   ├─→ Embedded Evaluations (automatic)
    │               │   ├─→ Quality Assurance (automatic)
    │               │   └─→ Multi-LLM Critique
    │               │
    │               ├─→ Agent Orchestration
    │               │   ├─→ Route to Generate Agent
    │               │   ├─→ Route to Judge Agent
    │               │   └─→ Multi-agent workflows
    │               │
    │               └─→ ACP Agent Registry
    │                       │
    │                       ├─→ Claude Code (via ACP)
    │                       ├─→ Codex (via ACP)
    │                       ├─→ Gemini CLI (via ACP)
    │                       └─→ Any ACP-compatible agent
    │
    └─→ Quality Feedback → Editor
```

### Multi-Agent Judge Flow

```
Editor Request
    │
    ├─→ CodeOptiX ACP Bridge
    │       │
    │       ├─→ Route to Generate Agent (Claude Code via ACP)
    │       │       └─→ Code Generated
    │       │
    │       ├─→ Route to Judge Agent (Grok/Codex via ACP)
    │       │       └─→ Code Judged
    │       │
    │       └─→ CodeOptiX Evaluates Both
    │               └─→ Quality Report → Editor
```

## Python API

### Using ACP Agent Registry

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

# Send prompt
response = await connection.prompt(
    session_id=session_id,
    prompt=[text_block("Write a secure login function")],
)
```

### Using Quality Bridge

```python
from codeoptix.acp import ACPQualityBridge
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client

# Create evaluation engine
llm_client = create_llm_client(LLMProvider.OPENAI)
evaluation_engine = EvaluationEngine(adapter, llm_client)

# Create quality bridge
bridge = ACPQualityBridge(
    agent_command=["python", "agent.py"],
    evaluation_engine=evaluation_engine,
    auto_eval=True,
    behaviors=["insecure-code", "vacuous-tests"],
)

# Connect and use
await bridge.connect()
result = await bridge.prompt("Write secure code")
```

### Using Multi-Agent Judge

```python
from codeoptix.acp import ACPAgentRegistry, MultiAgentJudge
from codeoptix.evaluation import EvaluationEngine

# Create registry and register agents
registry = ACPAgentRegistry()
registry.register(name="claude-code", command=["python", "claude_agent.py"])
registry.register(name="grok", command=["python", "grok_agent.py"])

# Create evaluation engine
evaluation_engine = EvaluationEngine(adapter, llm_client)

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

### Using Agent Orchestrator

```python
from codeoptix.acp import ACPAgentRegistry, AgentOrchestrator

# Create registry and orchestrator
registry = ACPAgentRegistry()
orchestrator = AgentOrchestrator(registry, evaluation_engine)

# Route to best agent
result = await orchestrator.route_to_agent(
    prompt="Write a test suite",
    context={"language": "python"},
)

# Execute multi-agent workflow
workflow = [
    {"agent": "claude-code", "prompt": "Generate code"},
    {"agent": "grok", "prompt": "Review the code"},
]
results = await orchestrator.execute_multi_agent_workflow(workflow)
```

## Code Extraction

CodeOptiX automatically extracts code from ACP messages, tool calls, and responses:

```python
from codeoptix.acp.code_extractor import extract_code_from_message, extract_all_code, extract_code_from_text

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
- ✅ Text content blocks (markdown code fences)
- ✅ File edit tool calls
- ✅ Tool call progress updates
- ✅ Agent message chunks
- ✅ Inline code patterns

## Real-time Quality Feedback

The quality bridge sends real-time feedback to your editor:

1. **Code Generation**: Agent generates code
2. **Code Extraction**: CodeOptiX automatically extracts code from messages, tool calls, and responses
3. **Quality Evaluation**: CodeOptiX evaluates code quality using the evaluation engine
4. **Feedback**: Quality report sent to editor via ACP session updates

The feedback includes:
- ✅/❌ Pass/fail status for each behavior
- Quality scores (percentage)
- Evidence of issues (specific examples)
- Recommendations for improvement
- Overall quality score

**Real-time Security Checks:**
The bridge also performs quick security checks in real-time, alerting immediately if potential security issues are detected (e.g., hardcoded secrets, API keys).

## Supported Editors

CodeOptiX works with any ACP-compatible editor:

- **Zed** - Native ACP support
- **JetBrains IDEs** - Via ACP plugin
- **Neovim** - Via ACP plugin
- **VS Code** - Via ACP extension
- **Any ACP-compatible client**

## Configuration

### Bridge Configuration

```bash
codeoptix acp bridge \
  --agent-name claude-code \
  --auto-eval \
  --behaviors insecure-code,vacuous-tests,plan-drift \
  --cwd /path/to/project
```

### Behavior Selection

Specify which behaviors to evaluate:

```bash
codeoptix acp bridge \
  --agent-name claude-code \
  --behaviors insecure-code,vacuous-tests
```

Available behaviors:
- `insecure-code` - Security vulnerabilities
- `vacuous-tests` - Low-quality tests
- `plan-drift` - Requirements alignment

## Examples

### Example 1: Basic Quality Bridge

```bash
# Register an agent
codeoptix acp registry add \
  --name my-agent \
  --command "python my_agent.py"

# Use as quality bridge
codeoptix acp bridge --agent-name my-agent
```

### Example 2: Multi-Agent Judge

```bash
# Register agents
codeoptix acp registry add --name claude-code --command "python claude.py"
codeoptix acp registry add --name grok --command "python grok.py"

# Use multi-agent judge
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write a secure password hashing function"
```

### Example 3: Editor Integration

1. Start CodeOptiX as agent:
   ```bash
   codeoptix acp register
   ```

2. In your editor (e.g., Zed), connect to CodeOptiX via ACP

3. CodeOptiX will automatically evaluate code quality

## Advanced Features

### Custom Evaluation Behaviors

```python
from codeoptix.acp import ACPQualityBridge

bridge = ACPQualityBridge(
    agent_command=["python", "agent.py"],
    behaviors=["insecure-code", "custom-behavior"],  # Custom behaviors
    auto_eval=True,
)
```

### Agent Orchestration

```python
from codeoptix.acp import AgentOrchestrator

orchestrator = AgentOrchestrator(registry, evaluation_engine)

# Intelligent agent selection based on:
# - Agent capabilities (from registry)
# - Task type (inferred from prompt)
# - Context requirements
result = await orchestrator.route_to_agent(
    prompt="Write secure Python code",
    context={"language": "python", "task": "security", "preferred_agent": "claude-code"},
)

# The orchestrator will:
# 1. Check for preferred_agent in context
# 2. Infer task type (security, review, testing, etc.)
# 3. Match agents with relevant capabilities
# 4. Fall back to first available agent if no match
```

### Workflow Execution

```python
# Sequential workflow
workflow = [
    {"agent": "agent1", "prompt": "Step 1"},
    {"agent": "agent2", "prompt": "Step 2"},
]
results = await orchestrator.execute_multi_agent_workflow(workflow)
```

## Troubleshooting

### Agent Not Found

If you get "Agent not found" error:
1. Check agent is registered: `codeoptix acp registry list`
2. Register the agent: `codeoptix acp registry add --name <name> --command <cmd>`

### Connection Issues

If connection fails:
1. Verify agent command is correct
2. Check agent is ACP-compatible
3. Ensure agent process can be spawned

### Quality Evaluation Not Working

If quality evaluation doesn't run:
1. Ensure `--auto-eval` is enabled
2. Check evaluation engine is properly configured
3. Verify behaviors are specified correctly

## Best Practices

1. **Register agents in registry** - Easier management than direct commands
2. **Use specific behaviors** - Only evaluate behaviors you need
3. **Multi-agent judge** - Use for critical code that needs multiple perspectives
4. **Real-time feedback** - Enable auto-eval for immediate quality checks
5. **Agent selection** - Use orchestrator for intelligent agent routing

## See Also

- [CLI Usage Guide](../guides/cli-usage.md) - Complete CLI documentation
- [Python API Guide](../guides/python-api.md) - Python API usage
- [Behavior Specifications](../concepts/behaviors.md) - Behavior spec framework
- [Evaluation Engine](../concepts/evaluation.md) - Evaluation architecture

