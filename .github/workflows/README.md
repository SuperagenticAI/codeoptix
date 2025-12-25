# GitHub Actions Workflows

## CI Workflow

The CI workflow runs on every push and pull request to `main` and `develop` branches.

### Jobs

1. **Lint** - Runs code linting and formatting checks
   - Uses `ruff` for linting
   - Checks code formatting
   - Fails if code doesn't meet style standards

2. **Test** - Runs test suite
   - Uses `pytest` for testing
   - Generates coverage reports
   - Uploads coverage to Codecov (optional)

### Requirements

- Python 3.12
- `uv` for dependency management
- All dependencies from `pyproject.toml`

### Running Locally

To run the same checks locally:

```bash
# Linting
ruff check src/
ruff format --check src/

# Testing
pytest tests/ -v --cov=src/codeoptix
```

