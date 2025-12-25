# Ollama Integration Guide

CodeOptiX supports local Ollama models, allowing you to run evaluations without API keys!

---

## 🎯 Why Ollama?

- ✅ **No API key required** - Perfect for open-source users
- ✅ **Privacy-friendly** - All processing happens locally
- ✅ **Free to use** - No cloud costs
- ✅ **Works offline** - No internet connection needed
- ✅ **Flexible models** - Choose from many open-source models

---

## 📦 Installation

### Step 1: Install Ollama

Visit https://ollama.ai and install Ollama for your platform:

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### Step 2: Start Ollama Service

```bash
ollama serve
```

This starts the Ollama service on `http://localhost:11434` (default).

### Step 3: Pull a Model

Pull a model you want to use:

```bash
# Recommended models for CodeOptiX
ollama pull llama3.1:8b        # Fast, efficient (4.9 GB)
ollama pull qwen3:8b           # Alternative 8B model (5.2 GB)
ollama pull gpt-oss:120b       # Large, powerful (65 GB)
ollama pull gpt-oss:20b        # Medium model (13 GB)
ollama pull llama3.2:3b        # Lightweight (2.0 GB)
```

**See available models:**
```bash
ollama list
```

---

## 🚀 Quick Start

### Basic Usage

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider ollama
```

### With Configuration File

Create `ollama-config.yaml`:

```yaml
adapter:
  llm_config:
    provider: ollama
    model: llama3.1:8b  # Or gpt-oss:120b, qwen3:8b, etc.
    # No api_key needed!

evaluation:
  scenario_generator:
    num_scenarios: 2
    use_bloom: false

behaviors:
  insecure-code:
    enabled: true
```

Run:

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --config ollama-config.yaml \
  --llm-provider ollama
```

---

## ⚙️ Configuration

### In Config File

```yaml
adapter:
  llm_config:
    provider: ollama
    model: llama3.1:8b  # Choose your model
    # No api_key needed!
```

### Via Environment Variable

```bash
export CODEOPTIX_LLM_PROVIDER=ollama
codeoptix eval --agent claude-code --behaviors insecure-code
```

### Custom Ollama URL

By default, Ollama runs on `http://localhost:11434`. To use a different URL:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
# Or use a remote Ollama instance
export OLLAMA_BASE_URL=http://remote-server:11434
```

---

## 📋 Available Models

### Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.1:8b` | 4.9 GB | ⚡⚡⚡ | ⭐⭐⭐ | Fast, efficient |
| `qwen3:8b` | 5.2 GB | ⚡⚡⚡ | ⭐⭐⭐ | Alternative 8B |
| `gpt-oss:120b` | 65 GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |
| `gpt-oss:20b` | 13 GB | ⚡⚡ | ⭐⭐⭐⭐ | Good balance |
| `llama3.2:3b` | 2.0 GB | ⚡⚡⚡⚡ | ⭐⭐ | Lightweight |

### List Available Models

```bash
ollama list
```

### Pull a Model

```bash
ollama pull <model-name>
```

---

## 💡 Usage Examples

### Example 1: Basic Evaluation

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider ollama
```

### Example 2: With Custom Config

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --config examples/configs/ollama-insecure-code.yaml \
  --llm-provider ollama
```

### Example 3: Multiple Behaviors

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code,vacuous-tests \
  --llm-provider ollama
```

### Example 4: Verbose Output

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider ollama \
  --verbose
```

### Example 5: CI/CD Integration

```yaml
# .github/workflows/codeoptix.yml
name: CodeOptiX Check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Ollama
        run: |
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama pull llama3.1:8b
      - name: Install CodeOptiX
        run: pip install codeoptix
      - name: Run CodeOptiX
        run: |
          codeoptix ci \
            --agent claude-code \
            --behaviors insecure-code \
            --llm-provider ollama \
            --fail-on-failure
```

---

## 🔧 Troubleshooting

### Ollama Not Running

**Error:** `Failed to contact Ollama at http://localhost:11434`

**Solution:**
```bash
# Start Ollama service
ollama serve
```

### Model Not Found

**Error:** Model not available

**Solution:**
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify it's available
ollama list
```

### Connection Timeout

**Error:** Timeout when calling Ollama

**Solution:**
- Large models (like `gpt-oss:120b`) may take longer
- CodeOptiX uses a 300-second timeout by default
- Ensure you have enough RAM for the model
- Try a smaller model if timeouts persist

### Custom Port

If Ollama is running on a different port:

```bash
export OLLAMA_BASE_URL=http://localhost:11435
```

---

## 🆚 Ollama vs Cloud Providers

| Feature | Ollama | Cloud Providers |
|---------|--------|-----------------|
| API Key | ❌ Not required | ✅ Required |
| Cost | ✅ Free | ⚠️ Pay per use |
| Privacy | ✅ Local only | ⚠️ Data sent externally |
| Internet | ✅ Works offline | ❌ Requires connection |
| Setup | ⚠️ Install Ollama | ✅ Just API key |
| Models | ⚠️ Limited to local | ✅ Many options |
| Speed | ⚠️ Depends on hardware | ✅ Fast (cloud) |

**Choose Ollama if:**
- You want privacy
- You want to avoid API costs
- You have sufficient local compute
- You want to work offline

**Choose Cloud Providers if:**
- You need the latest models
- You don't have local compute
- You need maximum speed
- You're okay with API costs

---

## 📚 Next Steps

- [Quick Start Guide](../getting-started/quickstart.md)
- [Configuration Guide](configuration.md)
- [Behavior Specifications](../concepts/behaviors.md)
- [GEPA Optimization](../advanced/gepa.md)
- [Bloom Evaluations](../advanced/bloom.md)

---

## 🐛 Issues?

If you encounter problems:

1. Check [Troubleshooting](#troubleshooting) above
2. Verify Ollama is running: `ollama list`
3. Check model is pulled: `ollama list`
4. Open an issue on [GitHub](https://github.com/SuperagenticAI/codeoptix/issues)

