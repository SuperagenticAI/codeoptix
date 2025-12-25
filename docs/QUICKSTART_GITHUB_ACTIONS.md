# Quick Start: CodeOptiX in GitHub Actions

Get CodeOptiX running in your CI/CD pipeline in 5 minutes.

## Step 1: Add Workflow File

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
            --behaviors insecure-code \
            --llm-provider openai \
            --fail-on-failure
```

## Step 2: Add API Key Secret

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click **Add secret**

## Step 3: Test It

1. Create a pull request
2. The workflow will automatically run
3. Check the **Actions** tab to see results

## What It Does

- ✅ Runs on every pull request
- ✅ Checks for security issues (hardcoded secrets, SQL injection, etc.)
- ✅ Fails the build if security issues are found
- ✅ Shows results in the Actions tab

## Customize

### Check Multiple Behaviors

```yaml
codeoptix eval \
  --behaviors insecure-code,vacuous-tests,plan-drift \
  --llm-provider openai \
  --fail-on-failure
```

### Use Different Agent

```yaml
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider anthropic \
  --fail-on-failure
```

### Add Context

```yaml
codeoptix eval \
  --agent codex \
  --behaviors plan-drift \
  --context '{"plan_file": "planning.md"}' \
  --llm-provider openai \
  --fail-on-failure
```

## Next Steps

- See [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) for advanced usage
- Check [examples/](examples/) for more scenarios
- Read [BEHAVIOR_SPECS.md](concepts/behaviors.md) for available behaviors

