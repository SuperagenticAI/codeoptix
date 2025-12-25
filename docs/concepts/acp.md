# ACP (Agent Client Protocol) Integration

CodeOptiX provides comprehensive ACP integration for editor support, multi-agent workflows, and code optimization.

## Overview

ACP (Agent Client Protocol) is a protocol for connecting AI agents to editors and other clients. CodeOptiX uses ACP to:

- **Act as an ACP agent** - Be used directly by editors (Zed, JetBrains, Neovim, VS Code)
- **Connect to other agents** - Use any ACP-compatible agent via the protocol
- **Quality bridge** - Sit between editor and agents, automatically evaluating code quality
- **Multi-agent orchestration** - Route to best agent for each task
- **Multi-agent judge** - Use different agents for generation vs. judgment

## Architecture

### Quality Bridge Mode

CodeOptiX acts as a quality bridge between your editor and coding agents:

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

## Components

### ACP Agent Registry

**Purpose**: Register and manage multiple ACP-compatible agents

**Features**:
- Register agents with commands and configurations
- Connect/disconnect from agents
- Session management
- Agent discovery

**Usage**:
```python
from codeoptix.acp import ACPAgentRegistry

registry = ACPAgentRegistry()
registry.register(
    name="claude-code",
    command=["python", "claude_agent.py"],
    description="Claude Code via ACP",
)
```

### Quality Bridge

**Purpose**: Automatic quality evaluation between editor and agents

**Features**:
- ✅ Automatic code extraction from agent messages, tool calls, and responses
- ✅ Real-time quality evaluation using evaluation engine
- ✅ Quality feedback to editor via ACP session updates
- ✅ Configurable behavior evaluation
- ✅ Quick security checks for immediate feedback
- ✅ Formatted quality reports with scores and evidence

**Quality Evaluation Process:**
1. Agent generates code
2. CodeOptiX extracts code from all sources
3. Evaluation engine evaluates against behavior specifications
4. Formatted report sent to editor with:
   - Overall quality score
   - Per-behavior pass/fail status
   - Evidence of issues
   - Recommendations

**Usage**:
```python
from codeoptix.acp import ACPQualityBridge
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client

# Create evaluation engine
llm_client = create_llm_client(LLMProvider.OPENAI)
evaluation_engine = EvaluationEngine(adapter, llm_client)

bridge = ACPQualityBridge(
    agent_name="claude-code",
    evaluation_engine=evaluation_engine,
    auto_eval=True,
    behaviors=["insecure-code", "vacuous-tests", "plan-drift"],
)

# Connect and use
await bridge.connect()
result = await bridge.prompt("Write secure authentication code")
```

### Agent Orchestrator

**Purpose**: Route to best agent for each task

**Features**:
- ✅ Intelligent agent selection based on capabilities and task type
- ✅ Multi-agent workflows
- ✅ Task-based routing
- ✅ Context-aware selection
- ✅ Automatic fallback to available agents

**Intelligent Selection Logic:**
1. Checks for `preferred_agent` in context
2. Infers task type from prompt keywords (security, review, testing, etc.)
3. Matches agents with relevant capabilities from registry
4. Falls back to first available agent if no match

**Usage**:
```python
from codeoptix.acp import AgentOrchestrator

orchestrator = AgentOrchestrator(registry, evaluation_engine)

# Automatic intelligent selection
result = await orchestrator.route_to_agent(
    prompt="Write secure authentication tests",
    context={"language": "python"}
)

# With preferred agent
result = await orchestrator.route_to_agent(
    prompt="Review this code",
    context={"preferred_agent": "grok"}
)
```

### Multi-Agent Judge

**Purpose**: Use different agents for generation vs. judgment

**Features**:
- ✅ Separate generate and judge agents
- ✅ Combined evaluation with CodeOptiX
- ✅ Multi-perspective assessment
- ✅ Code extraction from both agents
- ✅ Comprehensive quality reports

**Process:**
1. Generate code with generate agent
2. Extract code from generate agent response
3. Judge/critique code with judge agent
4. Extract judgment text from judge agent
5. Evaluate both with CodeOptiX evaluation engine
6. Return combined results

**Usage**:
```python
from codeoptix.acp import MultiAgentJudge

judge = MultiAgentJudge(
    registry=registry,
    generate_agent="claude-code",
    judge_agent="grok",
    evaluation_engine=evaluation_engine,
)

result = await judge.generate_and_judge("Write secure code")

# Result contains:
# {
#     "generated_code": "...",
#     "judgment": "...",
#     "evaluation_results": {...},
#     "generate_agent": "claude-code",
#     "judge_agent": "grok"
# }
```

### Code Extraction

**Purpose**: Extract code from ACP messages, tool calls, and responses

**Features**:
- ✅ Extract from text blocks (markdown code fences)
- ✅ Extract from file edits (old_text, new_text)
- ✅ Extract from tool calls (file_edit, etc.)
- ✅ Extract from tool call progress updates
- ✅ Pattern matching for code blocks (fenced and inline)
- ✅ Language detection
- ✅ Multiple extraction methods

**Supported Sources:**
- `AgentMessageChunk` - Agent message content
- `ToolCallStart` - Tool call initiation
- `ToolCallProgress` - Tool call progress updates
- `TextContentBlock` - Text content with code
- Raw text strings - Direct text extraction

**Usage**:
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

# Extract from text
code_blocks = extract_code_from_text("```python\ndef hello():\n    pass\n```")

# Each code block contains:
# {
#     "language": "python",
#     "content": "def hello():\n    pass",
#     "type": "block",  # or "inline", "file_edit_new", "file_edit_old"
#     "path": "file.py"  # if from file edit
# }
```

## Data Flow

### Quality Bridge Flow

1. **Editor Request**: Editor sends request via ACP
2. **Bridge Receives**: CodeOptiX bridge receives request
3. **Agent Execution**: Request routed to agent
4. **Code Extraction**: Code extracted from agent response
5. **Quality Evaluation**: CodeOptiX evaluates code quality
6. **Feedback**: Quality report sent to editor

### Multi-Agent Judge Flow

1. **Generate**: Code generated with generate agent
2. **Judge**: Code judged/critiqued with judge agent
3. **Evaluate**: CodeOptiX evaluates both perspectives
4. **Report**: Combined quality report sent to editor

## Use Cases

### Editor Integration

Connect CodeOptiX directly to your editor:

```bash
codeoptix acp register
# Connect from editor (Zed, JetBrains, Neovim, VS Code)
```

### Quality Bridge

Automatic quality checks for any agent:

```bash
codeoptix acp bridge --agent-name claude-code --auto-eval
```

### Multi-Agent Workflows

Orchestrate multiple agents:

```python
workflow = [
    {"agent": "claude-code", "prompt": "Generate code"},
    {"agent": "grok", "prompt": "Review code"},
]
results = await orchestrator.execute_multi_agent_workflow(workflow)
```

### Multi-Perspective Evaluation

Get multiple perspectives on code:

```bash
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write secure code"
```

## Benefits

1. **Real-time Feedback**: Quality feedback directly in editor
2. **No Context Switching**: Stay in your editor
3. **Automatic Evaluation**: Quality checks happen automatically
4. **Multi-Agent Support**: Use best agent for each task
5. **Editor Agnostic**: Works with any ACP-compatible editor

## See Also

- [ACP Integration Guide](../guides/acp-integration.md) - Complete ACP documentation
- [CLI Usage Guide](../guides/cli-usage.md) - ACP CLI commands
- [Python API Guide](../guides/python-api.md) - ACP Python API

