# Contributing to CodeOptiX

Thank you for your interest in contributing to CodeOptiX! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/SuperagenticAI/codeoptix.git
cd codeoptix

# Install with uv (recommended)
uv sync --dev --extra docs

# Or with pip
pip install -e ".[dev,docs]"

# Install pre-commit hooks
uv run pre-commit install
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=codeoptix --cov-report=html

# Run specific test file
uv run pytest tests/test_evaluation.py -v
```

### Code Quality

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit. To run manually:

```bash
uv run pre-commit run --all-files
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and ensure:
   - Tests pass (`uv run pytest`)
   - Code is formatted (`uv run ruff format .`)
   - Linting passes (`uv run ruff check .`)
4. **Commit** your changes with a descriptive message
5. **Push** to your fork
6. **Open a Pull Request** against `main`

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters

Examples:
- `Add support for custom behaviors`
- `Fix evaluation engine timeout handling`
- `Update documentation for CLI usage`

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for function signatures
- Write docstrings for public functions and classes (Google style)
- Keep functions focused and small

## Testing

- Write tests for new features
- Maintain or improve test coverage
- Use pytest fixtures for common test setup
- Test files should be in `tests/` directory

## Documentation

- Update documentation for user-facing changes
- Documentation is in `docs/` using MkDocs
- Preview docs locally: `uv run mkdocs serve`

## Questions?

- Open a [GitHub Discussion](https://github.com/SuperagenticAI/codeoptix/discussions)
- Check existing [Issues](https://github.com/SuperagenticAI/codeoptix/issues)

Thank you for contributing!
