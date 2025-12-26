<div align="center">

<img src="https://raw.githubusercontent.com/SuperagenticAI/codeoptix/main/docs/assets/CodeOptiX_Logo.png" alt="CodeOptiX Logo" width="200">

# CodeOptiX

**Agentic Code Optimization. Elevated Agent Experience.**

*Code Optimization Engine for every coding agent. Powered by Agent Optimizers like GEPA (Genetic-Pareto) and Bloom-style scenario generation for behavior testing.*

[![PyPI version](https://badge.fury.io/py/codeoptix.svg)](https://pypi.org/project/codeoptix/)
[![CI](https://github.com/SuperagenticAI/codeoptix/actions/workflows/ci.yml/badge.svg)](https://github.com/SuperagenticAI/codeoptix/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/SuperagenticAI/codeoptix/branch/main/graph/badge.svg)](https://codecov.io/gh/SuperagenticAI/codeoptix)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Documentation](https://superagenticai.github.io/codeoptix) |
[Get Started](#-quick-start) |
[Examples](https://github.com/SuperagenticAI/codeoptix/tree/main/examples) |
[Contributing](#-contributing)

</div>

---

## What is CodeOptiX?

CodeOptiX is an **open-source agentic code optimization platform** for evaluating, testing, and improving AI coding agents. Built by [Superagentic AI](https://super-agentic.ai).

### Key Features

- **GEPA Optimization** - Automatically improve agent behavior using Genetic-Pareto Evolution
- **Bloom Evaluations** - Deep behavioral evaluation with Bloom-style scenario generation
- **Behavior Testing** - Test coding agents against configurable behavior specifications
- **Agent-Agnostic** - Works with Claude Code, Codex, Gemini CLI, and any ACP-compatible agent
- **Multi-Provider** - Supports OpenAI, Anthropic, Google, and Ollama (local, no API key!)
- **CI/CD Ready** - GitHub Actions integration for automated quality gates

---

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv pip install codeoptix

# Using pip
pip install codeoptix
```

### Your First Evaluation

**Option 1: Using Ollama (No API Key Required)**

```bash
# Make sure Ollama is running
ollama serve

# Run evaluation with local model
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider ollama
```

**Option 2: Using Cloud Providers**

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run evaluation
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider openai
```

---

## Built-in Behaviors

| Behavior | Description |
|----------|-------------|
| `insecure-code` | Detects security vulnerabilities (SQL injection, XSS, hardcoded secrets) |
| `vacuous-tests` | Identifies low-quality tests (missing assertions, trivial tests) |
| `plan-drift` | Detects requirements misalignment and plan deviations |

```bash
# Run multiple behaviors
codeoptix eval --behaviors insecure-code,vacuous-tests,plan-drift
```

---

## Usage Modes

### CLI Evaluation

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider openai
```

### CI/CD Integration

```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --fail-on-failure
```

### Python API

```python
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider

# Create adapter and evaluation engine
adapter = create_adapter("claude-code", config)
llm_client = create_llm_client(LLMProvider.OPENAI)
engine = EvaluationEngine(adapter, llm_client)

# Evaluate behaviors
results = engine.evaluate_behaviors(
    behavior_names=["insecure-code", "vacuous-tests"]
)
```

---

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/SuperagenticAI/codeoptix.git
cd codeoptix

# Install with uv (recommended)
uv sync --dev --extra docs

# Or with pip
pip install -e ".[dev,docs]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=codeoptix --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Install pre-commit hooks
uv run pre-commit install
```

---

## Contributing

Contributions are welcome! Please see our [Contributing Guide](https://github.com/SuperagenticAI/codeoptix/blob/main/CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/SuperagenticAI/codeoptix/blob/main/LICENSE) file for details.

---

## Support

- [Documentation](https://superagenticai.github.io/codeoptix)
- [GitHub Issues](https://github.com/SuperagenticAI/codeoptix/issues)
- [GitHub Discussions](https://github.com/SuperagenticAI/codeoptix/discussions)

---

<div align="center">

**Brought to you by [Superagentic AI](https://super-agentic.ai)**

</div>
