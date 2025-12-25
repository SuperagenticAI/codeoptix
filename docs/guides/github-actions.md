# GitHub Actions Integration

Complete guide to using CodeOptiX in GitHub Actions CI/CD pipelines.

---

## Quick Start

### 1. Add Workflow File

Create `.github/workflows/codeoptix.yml`:

```yaml
name: CodeOptiX Check

on:
  pull_request:
    branches: [ main ]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - uses: astral-sh/setup-uv@v4
      
      - run: uv sync --dev
      
      - name: Run CodeOptiX
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codeoptix eval \
            --agent codex \
            --behaviors insecure-code \
            --llm-provider openai \
            --fail-on-failure
```

### 2. Configure Secrets

Add your API key as a GitHub Secret:
1. Go to repository Settings → Secrets and variables → Actions
2. Add `OPENAI_API_KEY` secret
3. The workflow will use it automatically

---

## Basic Workflow

### Simple Check

```yaml
- name: Run CodeOptiX
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    codeoptix eval \
      --agent codex \
      --behaviors insecure-code \
      --llm-provider openai \
      --fail-on-failure
```

---

## Full Pipeline

### Complete Workflow

```yaml
name: CodeOptiX Full Pipeline

on:
  pull_request:
    branches: [ main ]

jobs:
  codeoptix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - uses: astral-sh/setup-uv@v4
      
      - run: uv sync --dev
      
      - name: Run Evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codeoptix eval \
            --agent codex \
            --behaviors insecure-code,vacuous-tests \
            --llm-provider openai \
            --output .codeoptix/results.json
      
      - name: Generate Reflection
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codeoptix reflect \
            --input .codeoptix/results.json \
            --output .codeoptix/reflection.md
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: codeoptix-results
          path: .codeoptix/
```

---

## PR Comments

### Post Results as PR Comment

```yaml
- name: Comment PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      const fs = require('fs');
      const results = JSON.parse(fs.readFileSync('.codeoptix/results.json', 'utf8'));
      
      let comment = '## CodeOptiX Results\n\n';
      for (const [name, data] of Object.entries(results.behaviors || {})) {
        comment += `- ${data.passed ? '✅' : '❌'} ${name}\n`;
      }
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

---

## Best Practices

### 1. Use Secrets

Never hardcode API keys:

```yaml
# ✅ Good
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

# ❌ Bad
env:
  OPENAI_API_KEY: sk-...
```

### 2. Fail on Critical Behaviors

Use `--fail-on-failure` for security checks:

```yaml
codeoptix eval \
  --behaviors insecure-code \
  --fail-on-failure
```

### 3. Upload Artifacts

Always upload results for debugging:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: codeoptix-results
    path: .codeoptix/
```

---

## Advanced Examples

### Matrix Strategy

Test with multiple agents:

```yaml
strategy:
  matrix:
    agent: [codex, claude-code, gemini-cli]
steps:
  - name: Run CodeOptiX
    run: |
      codeoptix eval --agent ${{ matrix.agent }}
```

### Conditional Execution

Only run on Python files:

```yaml
- name: Check if Python files changed
  id: changed-files
  uses: tj-actions/changed-files@v40
  with:
    files: |
      **/*.py

- name: Run CodeOptiX
  if: steps.changed-files.outputs.any_changed == 'true'
  run: |
    codeoptix eval --behaviors insecure-code
```

---

## Troubleshooting

### API Key Issues

Check secrets are set correctly in repository settings.

### Timeout Issues

Reduce scenarios or use faster models:

```yaml
codeoptix eval \
  --behaviors insecure-code \
  --config config.yaml  # With reduced scenarios
```

---

## Next Steps

- [CLI Usage Guide](cli-usage.md) - All CLI commands
- [Configuration Guide](configuration.md) - Advanced configuration
- [Python API Guide](python-api.md) - Python integration

