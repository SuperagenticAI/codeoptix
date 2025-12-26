# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Agentic Code Optimization. Elevated Agent Experience.**

CodeOptiX is an agentic code optimization platform that evaluates, reflects on, and evolves the behavior of coding AI agents (Claude Code, Codex, Gemini CLI). It uses a workflow of **Observe → Evaluate → Reflect → Evolve** with multi-modal evaluation (static analysis + LLM judgment + test results).

## Common Commands

```bash
# Install with dev dependencies
pip install -e ".[dev,docs]"
# OR with uv (faster)
uv sync --dev --extra docs

# Run all tests
pytest

# Run single test file
pytest tests/test_evaluation.py

# Run with coverage
pytest --cov=codeoptix --cov-report=html

# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/codeoptix

# Security check
bandit -r src/codeoptix

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run CLI evaluation
codeoptix eval --agent claude-code --behaviors insecure-code --llm-provider openai

# CI mode (fails on issues)
codeoptix ci --agent claude-code --behaviors insecure-code --fail-on-failure
```

## Architecture

### Core Engines

The codebase follows a modular engine-based architecture:

- **Adapters** (`src/codeoptix/adapters/`): Standardized interface for coding agents. `AgentAdapter` base class with `ClaudeCodeAdapter`, `CodexAdapter`, `GeminiCLIAdapter` implementations. Use `create_adapter()` factory.

- **Behaviors** (`src/codeoptix/behaviors/`): Modular behavior definitions for evaluation. `BehaviorSpec` base class with built-in `InsecureCodeBehavior`, `VacuousTestsBehavior`, `PlanDriftBehavior`. Use `create_behavior()` factory.

- **Evaluation Engine** (`src/codeoptix/evaluation/`): Orchestrates multi-modal evaluation. `EvaluationEngine` coordinates `ScenarioGenerator`, `StaticAnalyzer`, `LLMEvaluator`, `TestRunner`.

- **Reflection Engine** (`src/codeoptix/reflection/`): Analyzes results and generates insights. Produces markdown reports with actionable recommendations.

- **Evolution Engine** (`src/codeoptix/evolution/`): GEPA-style prompt optimization. `EvolutionEngine` uses `PromptProposer` to generate and evaluate prompt mutations.

- **Linters** (`src/codeoptix/linters/`): Multi-linter orchestration via `LinterRunner`. Individual linters (Ruff, Bandit, MyPy, etc.) extend `BaseLinter`.

- **ACP** (`src/codeoptix/acp/`): Agent Client Protocol integration for editor workflows.

### Key Patterns

- **Factory pattern**: `create_adapter()`, `create_behavior()`, `create_llm_client()`
- **Abstract base classes**: Extend `AgentAdapter`, `BehaviorSpec`, `BaseLinter` for customization
- **Configuration-driven**: All engines accept config dictionaries
- **LLM provider abstraction**: Supports Anthropic, OpenAI, Google, Ollama via `LLMClient`

### Data Flow

1. Agent adapter executes task → returns `AgentOutput` (code, tests, traces)
2. Behaviors evaluate output → return `BehaviorResult` (passed, score, evidence, severity)
3. Evaluation engine aggregates results → stores via `ArtifactManager`
4. Reflection engine analyzes → generates markdown insights
5. Evolution engine proposes → iterates on prompts

## CLI Entry Point

Main CLI is in `src/codeoptix/cli.py`. Commands: `eval`, `ci`, `reflect`, `evolve`, `lint`, `acp`.

## Python API Entry Points

```python
from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.reflection import ReflectionEngine
from codeoptix.evolution import EvolutionEngine
from codeoptix.utils.llm import create_llm_client, LLMProvider
```

## LLM Providers

Supports multiple providers via the `--llm-provider` flag or `LLMProvider` enum:
- `openai` - GPT-4, GPT-4o
- `anthropic` - Claude models
- `google` - Gemini models
- `ollama` - Local models (no API key required)

## Test Configuration

Tests are in `tests/` with pytest. Fixtures in `conftest.py`. Run specific tests with `pytest tests/test_<module>.py -v`.
