# CodeOptiX Example Configurations

This directory contains example configuration files for different use cases.

## Quick Start

### Single Behavior (Recommended for Open-Source)

Start with a single behavior to get familiar with CodeOptiX:

```bash
# Security check only
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --config examples/configs/single-behavior-insecure-code.yaml

# Test quality check only
codeoptix eval \
  --agent claude-code \
  --behaviors vacuous-tests \
  --config examples/configs/single-behavior-vacuous-tests.yaml

# Plan alignment check only
codeoptix eval \
  --agent claude-code \
  --behaviors plan-drift \
  --config examples/configs/single-behavior-plan-drift.yaml
```

### CI/CD Mode

Use the CI/CD configuration for GitHub Actions:

```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --config examples/configs/ci-cd.yaml \
  --fail-on-failure
```

### Basic Configuration

Minimal configuration for getting started:

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --config examples/configs/basic.yaml
```

## Configuration Files

### `basic.yaml`
- Minimal configuration
- Single behavior
- Fast execution
- **Best for**: First-time users

### `single-behavior-insecure-code.yaml`
- Security checks only
- Static analysis enabled
- **Best for**: Security-focused projects

### `single-behavior-vacuous-tests.yaml`
- Test quality checks only
- **Best for**: Projects with test suites

### `single-behavior-plan-drift.yaml`
- Requirements alignment only
- **Best for**: Projects with clear requirements

### `ci-cd.yaml`
- Optimized for CI/CD
- Fast execution
- Security-focused
- **Best for**: GitHub Actions, CI pipelines

## Environment Variables

All configurations use environment variables for API keys:

```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"  # For Claude Code
export GOOGLE_API_KEY="your-key-here"     # For Gemini
```

## Customization

You can copy any configuration file and modify it:

```bash
cp examples/configs/basic.yaml my-config.yaml
# Edit my-config.yaml
codeoptix eval --agent claude-code --behaviors insecure-code --config my-config.yaml
```

