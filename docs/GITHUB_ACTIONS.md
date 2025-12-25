# Using CodeOptiX in GitHub Actions

This guide shows how to integrate CodeOptiX into your CI/CD pipeline to automatically check agent behavior.

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
        with:
          version: "latest"
      
      - run: uv sync --dev
      
      - name: Run CodeOptiX
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codeoptix eval \
            --agent codex \
            --behaviors insecure-code,vacuous-tests \
            --llm-provider openai \
            --fail-on-failure
```

### 2. Configure Secrets

Add your API keys as GitHub Secrets:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add secrets:
   - `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`)
3. The workflow will automatically use these secrets

### 3. Run Checks

The workflow will:
- ✅ Run on every pull request
- ✅ Evaluate agent behavior
- ✅ Fail the build if behaviors don't pass
- ✅ Upload results as artifacts

## Workflow Examples

### Basic Check

Simple evaluation that fails if behaviors don't pass:

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

### Full Pipeline

Complete workflow with evaluation, reflection, and artifact upload:

```yaml
- name: Run Evaluation
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    codeoptix eval \
      --agent codex \
      --behaviors insecure-code,vacuous-tests,plan-drift \
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

### With PR Comments

Post results as PR comments:

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

## Behavior Specifications

### Code Security

Check for security issues:

```yaml
codeoptix eval \
  --behaviors insecure-code \
  --context '{"check_secrets": true, "check_sql_injection": true}'
```

### Test Quality

Check test quality:

```yaml
codeoptix eval \
  --behaviors vacuous-tests \
  --context '{"require_assertions": true, "check_coverage": true}'
```

### Plan Alignment

Check against planning documents:

```yaml
codeoptix eval \
  --behaviors plan-drift \
  --context '{"plan_file": "planning.md"}'
```

### Multiple Behaviors

Check multiple behaviors at once:

```yaml
codeoptix eval \
  --behaviors insecure-code,vacuous-tests,plan-drift \
  --llm-provider openai
```

## Configuration Options

### Using Config File

Create `codeoptix.yaml`:

```yaml
adapter:
  llm_config:
    provider: openai
    model: gpt-4o
    api_key: ${OPENAI_API_KEY}

evaluation:
  behaviors:
    - insecure-code
    - vacuous-tests
  scenario_generator:
    num_scenarios: 3
```

Then use in workflow:

```yaml
- name: Run CodeOptiX
  run: |
    codeoptix eval --config codeoptix.yaml
```

### Environment Variables

Set configuration via environment:

```yaml
- name: Run CodeOptiX
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    CODEFLECT_BEHAVIORS: insecure-code,vacuous-tests
    CODEFLECT_AGENT: codex
  run: |
    codeoptix eval
```

## Advanced Usage

### Conditional Execution

Only run on specific files:

```yaml
- name: Check if Python files changed
  id: changed-files
  uses: tj-actions/changed-files@v40
  with:
    files: |
      **/*.py
      **/*.md

- name: Run CodeOptiX
  if: steps.changed-files.outputs.any_changed == 'true'
  run: |
    codeoptix eval --behaviors insecure-code
```

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

### Caching

Cache CodeOptiX artifacts:

```yaml
- name: Cache artifacts
  uses: actions/cache@v3
  with:
    path: .codeoptix/
    key: codeoptix-${{ github.sha }}

- name: Run CodeOptiX
  run: |
    codeoptix eval --behaviors insecure-code
```

## Best Practices

### 1. Use Secrets for API Keys

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
  --fail-on-failure  # Fails build if insecure-code fails
```

### 3. Upload Artifacts

Always upload results for debugging:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: codeoptix-results
    path: .codeoptix/
```

### 4. Set Timeout

Prevent long-running evaluations:

```yaml
- name: Run CodeOptiX
  timeout-minutes: 10
  run: |
    codeoptix eval --behaviors insecure-code
```

### 5. Use Specific Behaviors

Only check relevant behaviors:

```yaml
# ✅ Good - specific
codeoptix eval --behaviors insecure-code

# ⚠️  Less efficient - all behaviors
codeoptix eval --behaviors insecure-code,vacuous-tests,plan-drift
```

## Troubleshooting

### API Key Issues

If you see authentication errors:

1. Check secrets are set correctly
2. Verify API key has correct permissions
3. Check rate limits

### Timeout Issues

If evaluations timeout:

1. Reduce number of scenarios: `--scenarios 1`
2. Use faster models: `--model gpt-3.5-turbo`
3. Check only critical behaviors

### No Results

If no results are generated:

1. Check agent execution succeeded
2. Verify behaviors are valid
3. Check logs for errors

## Example Workflows

See `.github/workflows/` for complete examples:

- `codeoptix-check.yml` - Full featured workflow
- `codeoptix-simple.yml` - Minimal workflow

## Next Steps

1. Start with the simple workflow
2. Add behaviors as needed
3. Customize for your use case
4. Integrate with your existing CI/CD

