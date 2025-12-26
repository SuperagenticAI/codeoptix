# Installation

This guide will help you install CodeOptiX on your system.

---

## Prerequisites

Before installing CodeOptiX, make sure you have:

- **Python 3.12 or higher** - Check with `python --version`
- **pip** or **uv** - Python package manager
- **API Key** - From at least one LLM provider (OpenAI, Anthropic, or Google)

---

## Installation Methods

### Method 1: Using pip (Recommended for Beginners)

The simplest way to install CodeOptiX:

```bash
pip install codeoptix
```

### Method 2: Using uv (Faster)

If you have `uv` installed:

```bash
uv pip install codeoptix
```

### Method 3: From Source

For development or latest features:

```bash
# Clone the repository
git clone https://github.com/SuperagenticAI/codeoptix.git
cd codeoptix

# Install in development mode
pip install -e .
```

---

## Verify Installation

After installation, verify that CodeOptiX is installed correctly:

```bash
# Check version
codeoptix --version

# View help
codeoptix --help
```

You should see output like:

```
CodeOptiX, version 0.1.0
```

---

## Setting Up LLM Providers

CodeOptiX supports multiple LLM providers. Choose the one that works best for you:

### Option 1: Ollama (Recommended for Open-Source Users) 🆕

**No API key required!** Use local Ollama models:

```bash
# 1. Install Ollama: https://ollama.com
# 2. Start Ollama service
ollama serve

# 3. Pull a model
ollama pull llama3.1:8b

# 4. Use in CodeOptiX
codeoptix eval --agent basic --behaviors insecure-code --llm-provider ollama
```

**See [Ollama Integration Guide](../../guides/ollama-integration.md) for detailed setup.**

### Option 2: Cloud Providers (Requires API Keys)

CodeOptiX supports cloud LLM providers. Set at least one API key:

### OpenAI

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

### Google

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

!!! tip "Ollama vs Cloud Providers"
    **Ollama (Local):**
    - ✅ No API key required
    - ✅ Free to use
    - ✅ Privacy-friendly (runs locally)
    - ✅ Works offline
    - ⚠️ Requires local compute resources
    
    **Cloud Providers:**
    - ✅ More powerful models
    - ✅ No local compute needed
    - ⚠️ Requires API key
    - ⚠️ May incur costs
    - ⚠️ Data sent to external service

### Windows (PowerShell)

```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

### Windows (CMD)

```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

---

## Optional Dependencies

### Development Tools

For development and testing:

```bash
pip install codeoptix[dev]
```

Includes:
- `pytest` - Testing framework
- `ruff` - Code linter
- `mypy` - Type checker
- `black` - Code formatter

### Ollama Integration (Local LLM Support)

CodeOptiX supports local Ollama models - no API key required!

**Prerequisites:**
1. Install Ollama: https://ollama.com
2. Start Ollama service: `ollama serve`
3. Pull a model: `ollama pull llama3.1:8b` (or `gpt-oss:120b`, `qwen3:8b`, etc.)

**Usage:**
```bash
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider ollama \
  --config examples/configs/ollama-insecure-code.yaml
```

**Configuration:**
```yaml
adapter:
  llm_config:
    provider: ollama
    model: llama3.2:3b  # Or llama3.1:8b, gpt-oss:120b, qwen3:8b, etc.
    # No api_key needed!
```

**See [Ollama Integration Guide](../../guides/ollama-integration.md) for detailed setup and examples.**

---

## Troubleshooting

### Installation Fails

If installation fails, try:

```bash
# Upgrade pip first
pip install --upgrade pip

# Then install CodeOptiX
pip install codeoptix
```

### Import Errors

If you get import errors:

```bash
# Verify installation
pip show codeoptix

# Reinstall if needed
pip uninstall codeoptix
pip install codeoptix
```

### API Key Not Found

If CodeOptiX can't find your API key:

1. Check that the environment variable is set:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Make sure you're using the correct variable name
3. Restart your terminal after setting the variable

---

## Next Steps

Now that CodeOptiX is installed, you're ready to:

1. **[Quick Start](quickstart.md)** - Run your first evaluation
2. **[Your First Evaluation](first-evaluation.md)** - Detailed walkthrough
3. **[Python API Guide](../guides/python-api.md)** - Use CodeOptiX in Python

---

## Need Help?

If you encounter any issues:

- Check the [Troubleshooting](#troubleshooting) section above
- Open an issue on [GitHub](https://github.com/SuperagenticAI/codeoptix/issues)
- Join our [Discussions](https://github.com/SuperagenticAI/codeoptix/discussions)

