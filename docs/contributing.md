# Contributing to CodeOptiX

We welcome contributions! This guide will help you get started.

---

## How to Contribute

### Reporting Bugs

Found a bug? Please open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages and stack traces (if applicable)

### Suggesting Features

Have an idea? Open an issue with:
- Feature description
- Use case and motivation
- Proposed implementation (if any)
- Examples of how it would be used

### Submitting Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run pre-commit hooks (`pre-commit run --all-files`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

---

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SuperagenticAI/codeoptix.git
cd codeoptix
```

### 2. Install Dependencies

```bash
# Install in development mode with all dependencies
pip install -e ".[dev,docs]"

# Or with uv (recommended, faster)
uv sync --dev --extra docs
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit hooks (runs automatically on git commit)
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

---

## Code Quality

### Formatting and Linting

We use **Ruff** for both linting and formatting:

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Type Checking

We use **MyPy** for static type checking:

```bash
# Run type checker
mypy src/codeoptix

# With stricter settings (optional)
mypy src/codeoptix --strict
```

### Security Checks

We use **Bandit** for security vulnerability detection:

```bash
# Run security checks
bandit -r src/codeoptix
```

---

## Testing

All contributions should include tests:

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=codeoptix --cov-report=html

# Run specific test file
pytest tests/test_evaluation.py

# Run specific test
pytest tests/test_evaluation.py::test_specific_function
```

### Writing Tests

```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_value = "test"
    
    # Act
    result = function_under_test(input_value)
    
    # Assert
    assert result == expected
```

**Test Guidelines:**
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test both success and failure cases
- Test edge cases and boundaries
- Keep tests independent and isolated
- Use fixtures for common setup

---

## Code Style

We follow [PEP 8](https://peps.python.org/pep-0008/) style guide with some modifications:

### Key Style Guidelines

- **Line length**: 100 characters (enforced by Ruff)
- **Type hints**: Use type hints for function parameters and return types
- **Docstrings**: Use Google-style docstrings
- **Imports**: Sort imports with isort (handled by Ruff)

### Example

```python
from typing import List, Optional

def process_data(
    items: List[str],
    limit: Optional[int] = None
) -> List[str]:
    """Process a list of items.
    
    Args:
        items: List of items to process
        limit: Optional limit on number of items
        
    Returns:
        List of processed items
        
    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    
    # Process items
    processed = [item.upper() for item in items[:limit]]
    return processed
```

---

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality:

### Hooks Included

- **Trailing whitespace** - Removes trailing whitespace
- **End of file fixer** - Ensures files end with newline
- **YAML/TOML/JSON checker** - Validates file formats
- **Large file detection** - Prevents committing large files
- **Merge conflict detection** - Detects merge conflict markers
- **Private key detection** - Prevents committing secrets
- **Ruff** - Linting and formatting
- **MyPy** - Type checking
- **Bandit** - Security checks

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
```

### Skipping Hooks (Not Recommended)

```bash
# Skip hooks for a commit (use sparingly)
git commit --no-verify
```

---

## Documentation

Update documentation for new features:

### Documentation Structure

- **User Guides** (`docs/guides/`) - How-to guides for users
- **Concepts** (`docs/concepts/`) - Core concepts and architecture
- **Getting Started** (`docs/getting-started/`) - Beginner guides
- **Examples** (`examples/`) - Code examples
- **API Reference** (`docs/api-reference.md`) - API documentation

### Writing Documentation

1. Use clear, concise language
2. Include code examples
3. Add screenshots/diagrams when helpful
4. Keep it beginner-friendly
5. Update related sections

### Building Documentation

```bash
# Build documentation
mkdocs build

# Serve locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Commit Messages

Write clear, descriptive commit messages:

### Format

```
<type>: <subject>

<body>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat: add support for custom behavior specs

Allow users to define custom behavior specifications
through a configuration file.

Closes #123
```

```
fix: resolve issue with evaluation engine timeout

The evaluation engine was timing out on large codebases.
Increased timeout and added retry logic.

Fixes #456
```

---

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Run pre-commit hooks** (`pre-commit run --all-files`)
5. **Update CHANGELOG.md** (if applicable)
6. **Write clear PR description**:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Any breaking changes

---

## Questions?

- 📖 Check the [Documentation](index.md)
- 💬 Open a [Discussion](https://github.com/SuperagenticAI/codeoptix/discussions)
- 🐛 Search [Issues](https://github.com/SuperagenticAI/codeoptix/issues)
- 📧 Email: [codeoptix@super-agentic.ai](mailto:codeoptix@super-agentic.ai)

Thank you for contributing! 🎉
