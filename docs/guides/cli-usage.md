# CLI Usage Guide

Complete guide to using CodeOptiX from the command line.

---

## Installation

```bash
pip install codeoptix
# or
uv pip install codeoptix
```

---

## Commands

### `codeoptix eval` - Evaluate Agent Behavior

Evaluate a coding agent against behavior specifications.

**Basic Usage:**
```bash
codeoptix eval \
  --agent codex \
  --behaviors "insecure-code,vacuous-tests" \
  --llm-provider openai
```

**Options:**
- `--agent` (required): Agent type (`claude-code`, `codex`, `gemini-cli`)
- `--behaviors` (required): Comma-separated behavior names
- `--output`: Output file path (default: `results.json`)
- `--config`: Path to config file (JSON/YAML)
- `--llm-provider`: LLM provider (`anthropic`, `openai`, `google`, `ollama`)
- `--llm-api-key`: API key (or set environment variable)
- `--context`: Path to context file with plan/requirements (JSON)
- `--fail-on-failure`: Exit with error code if behaviors fail

**Available behaviors:**

- **`insecure-code`**: Detects insecure coding patterns (hardcoded secrets, SQL injection, etc.).

- **`vacuous-tests`**: Detects low-value tests (no assertions, trivial tests, etc.).

- **`plan-drift`**: Detects drift from a plan/requirements context.

**Example:**
```bash
export OPENAI_API_KEY="sk-..."
codeoptix eval \
  --agent codex \
  --behaviors "insecure-code,vacuous-tests" \
  --llm-provider openai \
  --context plan.json \
  --fail-on-failure
```

---

### `codeoptix ci` - CI/CD Mode

Run CodeOptiX in CI/CD mode, optimized for automation and pipelines.

**Basic Usage:**
```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai \
  --fail-on-failure
```

**Options:**
- `--agent` (required): Agent type (`claude-code`, `codex`, `gemini-cli`)
- `--behaviors` (required): Comma-separated behavior names
- `--config`: Path to config file (JSON/YAML)
- `--llm-provider`: LLM provider (`anthropic`, `openai`, `google`, `ollama`)
- `--llm-api-key`: API key (or set environment variable)
- `--fail-on-failure`: Exit with error code if behaviors fail (default: true)
- `--output-format`: Output format (`json` or `summary`, default: `json`)

**Features:**

- ✅ Non-interactive execution

- ✅ Proper exit codes for automation

- ✅ Summary output format

- ✅ Fail-fast behavior

- ✅ Optimized for CI/CD pipelines

**Example for GitHub Actions:**
```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai \
  --config examples/configs/ci-cd.yaml \
  --fail-on-failure \
  --output-format summary
```

**Output Formats:**

**JSON** (default):
```json
{
  "run_id": "run-001",
  "overall_score": 0.85,
  "behaviors": {
    "insecure-code": {
      "passed": true,
      "score": 0.85,
      "evidence": []
    }
  }
}
```

**Summary**:
```
📊 Evaluation Summary
Overall Score: 85.00%
Run ID: run-001

   ✅ **insecure-code**: 85.00%
```

---

### `codeoptix reflect` - Generate Reflection Report

Generate a human-readable reflection report from evaluation results.

**Basic Usage:**
```bash
codeoptix reflect --input results.json
```

**Options:**
- `--input` (required): Path to results JSON file or run ID
- `--output`: Output file path (default: `reflection_{run_id}.md`)
- `--agent-name`: Agent name for reflection report

**Example:**
```bash
codeoptix reflect \
  --input results.json \
  --output reflection.md \
  --agent-name codex
```

---

### `codeoptix evolve` - Evolve Agent Prompts

Automatically improve agent prompts based on evaluation results.

**Basic Usage:**
```bash
codeoptix evolve --input results.json
```

**Options:**
- `--input` (required): Path to results JSON file or run ID
- `--reflection`: Path to reflection markdown file (auto-generated if not provided)
- `--output`: Output file path (default: `evolved_prompts_{run_id}.yaml`)
- `--iterations`: Number of evolution iterations (default: 3)
- `--config`: Path to config file (JSON/YAML)

**Example:**
```bash
codeoptix evolve \
  --input results.json \
  --reflection reflection.md \
  --iterations 5 \
  --output evolved.yaml
```

---

### `codeoptix run` - Full Pipeline

Run the complete pipeline: evaluate → reflect → evolve (optional).

**Basic Usage:**
```bash
codeoptix run \
  --agent codex \
  --behaviors insecure-code \
  --evolve
```

**Options:**
- `--agent` (required): Agent type
- `--behaviors` (required): Comma-separated behavior names
- `--evolve`: Run evolution after evaluation
- `--config`: Path to config file

**Example:**
```bash
codeoptix run \
  --agent codex \
  --behaviors "insecure-code,vacuous-tests" \
  --evolve
```

---

### `codeoptix list-runs` - List Evaluation Runs

List all evaluation runs with their metadata.

**Usage:**
```bash
codeoptix list-runs
```

**Output:**
```
Found 3 evaluation run(s):

Run ID: abc123
  Timestamp: 2025-01-20T10:00:00Z
  Score: 0.75/1.0
  Behaviors: insecure-code, vacuous-tests

Run ID: def456
  Timestamp: 2025-01-20T11:00:00Z
  Score: 0.85/1.0
  Behaviors: insecure-code
```

---

### `codeoptix lint` - Static Analysis (No API Key Required)

Run static analysis linters on your code **without requiring an API key**.

!!! tip "Basic Mode - No API Key Required"
    The `lint` command works **without an API key** and uses basic static linters:

    - ✅ Security checks (Bandit, Safety, pip-audit)

    - ✅ Code quality (Ruff, Pylint, Flake8)

    - ✅ Type checking (mypy)

    - ✅ Test coverage (coverage.py)

    - ✅ Accessibility (HTML analyzer)
    
    **However, to unlock the full power** of CodeOptiX (behavioral evaluation, agent optimization, multi-LLM critique), **you need an API key**. See [Installation Guide](../getting-started/installation.md#setting-up-api-keys).

**Basic Usage:**
```bash
# Auto-detect language and linters
codeoptix lint --path ./src

# List available linters
codeoptix lint --list-linters

# Run specific linters
codeoptix lint --path ./src --linters ruff,bandit,mypy
```

**Options:**
- `--path` (required): Path to code (file or directory)
- `--linters`: Comma-separated linter names (default: auto-detect)
- `--output`: Output format (`json` or `summary`, default: `summary`)
- `--fail-on-issues`: Exit with non-zero code if issues found
- `--no-auto-detect`: Disable auto-detection of language and linters
- `--list-linters`: List all available linters and exit

**Example:**
```bash
# List available linters
codeoptix lint --list-linters

# Run on Python code
codeoptix lint --path ./src --linters ruff,bandit

# Check git changes
codeoptix check --base main --head feature
```

**Output:**
```
🔍 CodeOptiX Linter Check
============================================================
📁 Path: ./src
🔧 Linters: ruff, bandit
🚀 Running linters...

============================================================
📊 Linter Results Summary
============================================================
Total Issues: 15
  Critical: 2
  High: 5
  Medium: 8
  Low: 0

Execution Time: 2.34s

ruff: 8 issue(s)
bandit: 7 issue(s)
```

!!! important "Upgrade to Full Features"
    **The `lint` command provides basic static analysis only.**
    
    **To unlock CodeOptiX's full capabilities**, set an API key and use:
    - `codeoptix eval` - Behavioral evaluation of coding agents
    - `codeoptix reflect` - Deep quality analysis and insights
    - `codeoptix evolve` - Automatic prompt optimization
    
    **We strongly recommend setting up an API key** to experience CodeOptiX's full power.

---

### `codeoptix check` - Check Git Changes

Check code quality on git changes (no API key required).

**Basic Usage:**
```bash
codeoptix check --base main --head feature
```

**Options:**
- `--base`: Base branch/commit (default: `main`)
- `--head`: Head branch/commit (default: current branch)
- `--linters`: Comma-separated linter names (default: auto-detect)
- `--output`: Output format (`json` or `summary`)

**Example:**
```bash
# Check changes in current branch
codeoptix check

# Check specific branches
codeoptix check --base main --head feature-branch
```

---

## ACP (Agent Client Protocol) Commands

CodeOptiX provides ACP integration for editor support and multi-agent workflows.

### `codeoptix acp register` - Register as ACP Agent

Register CodeOptiX as an ACP agent for use with editors (Zed, JetBrains, Neovim, VS Code).

**Usage:**
```bash
codeoptix acp register
```

This starts CodeOptiX as an ACP agent. Connect from your editor using ACP protocol.

---

### `codeoptix acp bridge` - Quality Bridge

Use CodeOptiX as a quality bridge between editor and agents via ACP.

**Basic Usage:**
```bash
# Using agent from registry
codeoptix acp bridge --agent-name claude-code --auto-eval

# Using direct command
codeoptix acp bridge --agent-command "python agent.py" --auto-eval
```

**Options:**
- `--agent-command`: Command to spawn ACP agent (e.g., `"python agent.py"`)
- `--agent-name`: Name of agent in registry (alternative to `--agent-command`)
- `--auto-eval/--no-auto-eval`: Automatically evaluate code quality (default: `true`)
- `--behaviors`: Comma-separated behavior names to evaluate
- `--cwd`: Working directory for the agent

**Example:**
```bash
codeoptix acp bridge \
  --agent-name claude-code \
  --auto-eval \
  --behaviors "insecure-code,vacuous-tests"
```

---

### `codeoptix acp connect` - Connect to Agent

Connect to an ACP agent and send a prompt.

**Usage:**
```bash
codeoptix acp connect \
  --agent-name claude-code \
  --prompt "Write a secure login function"
```

**Options:**
- `--agent-command`: Command to spawn ACP agent
- `--agent-name`: Name of agent in registry
- `--prompt` (required): Prompt to send to agent
- `--cwd`: Working directory

---

### `codeoptix acp judge` - Multi-Agent Judge

Use different agents for generation vs. judgment.

**Usage:**
```bash
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write a secure API endpoint"
```

**Options:**
- `--generate-agent` (required): Agent name for code generation
- `--judge-agent` (required): Agent name for code judgment
- `--prompt` (required): Prompt for code generation

This will:
1. Generate code with the generate agent
2. Judge/critique the code with the judge agent
3. Evaluate both with CodeOptiX's evaluation engine

---

### `codeoptix acp registry` - Agent Registry Management

Manage ACP-compatible agents.

#### `codeoptix acp registry list` - List Agents

List all registered ACP agents.

**Usage:**
```bash
codeoptix acp registry list
```

#### `codeoptix acp registry add` - Register Agent

Register a new ACP agent.

**Usage:**
```bash
codeoptix acp registry add \
  --name claude-code \
  --command "python claude_agent.py" \
  --description "Claude Code via ACP" \
  --cwd /path/to/agent
```

**Options:**
- `--name` (required): Agent name
- `--command` (required): Command to spawn agent
- `--cwd`: Working directory
- `--description`: Agent description

#### `codeoptix acp registry remove` - Unregister Agent

Unregister an ACP agent.

**Usage:**
```bash
codeoptix acp registry remove --name claude-code
```

**Options:**
- `--name` (required): Agent name to remove

---

## ACP Workflows

### Editor Integration

1. **Start CodeOptiX as agent:**
   ```bash
   codeoptix acp register
   ```

2. **Connect from editor** (Zed, JetBrains, Neovim, VS Code) using ACP protocol

3. **CodeOptiX automatically evaluates** code quality in real-time

### Quality Bridge

1. **Register agents:**
   ```bash
   codeoptix acp registry add --name claude-code --command "python agent.py"
   ```

2. **Start quality bridge:**
   ```bash
   codeoptix acp bridge --agent-name claude-code --auto-eval
   ```

3. **Use from editor** - CodeOptiX automatically evaluates all agent interactions

### Multi-Agent Judge

```bash
# Register agents
codeoptix acp registry add --name claude-code --command "python claude.py"
codeoptix acp registry add --name grok --command "python grok.py"

# Use multi-agent judge
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write secure code"
```

---

## Configuration Files

You can use configuration files instead of command-line options.

### YAML Configuration

Create `codeoptix.yaml`:

```yaml
adapter:
  llm_config:
    provider: openai
    model: gpt-5.2
    api_key: ${OPENAI_API_KEY}

evaluation:
  scenario_generator:
    num_scenarios: 3
    use_bloom: true
  static_analysis:
    bandit: true

evolution:
  max_iterations: 3
  population_size: 3
```

Then use:

```bash
codeoptix eval --config codeoptix.yaml --agent codex --behaviors insecure-code
```

---

## Environment Variables

!!! important "API Key Required for Full Features"
    **Without an API key**, CodeOptiX runs in **basic mode** with static linters only (`codeoptix lint`, `codeoptix check`).
    
    **With an API key**, you unlock:

    - ✅ Behavioral evaluation (`codeoptix eval`)

    - ✅ Multi-LLM code critique

    - ✅ Automatic prompt optimization (`codeoptix evolve`)

    - ✅ Deep quality analysis (`codeoptix reflect`)

    - ✅ Agent orchestration and multi-agent workflows
    
    **We strongly recommend setting up an API key** to get the full CodeOptiX experience.

Set API keys as environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

---

## Common Workflows

### Quick Evaluation

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --llm-provider openai
```

### Full Pipeline

```bash
codeoptix run \
  --agent codex \
  --behaviors "insecure-code,vacuous-tests" \
  --evolve
```

### With Context

```bash
codeoptix eval \
  --agent codex \
  --behaviors "plan-drift" \
  --context plan.json
```

---

## Tips

### Use `--fail-on-failure` in CI/CD

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --fail-on-failure
```

### Save Results

Always specify output file:

```bash
codeoptix eval \
  --agent codex \
  --behaviors insecure-code \
  --output results.json
```

### Use Run IDs

You can use run IDs instead of file paths:

```bash
codeoptix reflect --input abc123
codeoptix evolve --input abc123
```

---

## Troubleshooting

### API Key Not Found

Make sure environment variable is set:

```bash
echo $OPENAI_API_KEY
```

### Agent Not Found

Check agent type is correct:
- `codex`
- `claude-code`
- `gemini-cli`

### Behavior Not Found

Use one of the built-in behaviors:

- **`insecure-code`**

- **`vacuous-tests`**

- **`plan-drift`**

---

## Next Steps

- [Python API Guide](python-api.md) - Use CodeOptiX in Python
- [ACP Integration Guide](acp-integration.md) - Complete ACP documentation
- [Configuration Guide](configuration.md) - Advanced configuration
- [GitHub Actions Guide](github-actions.md) - CI/CD integration

