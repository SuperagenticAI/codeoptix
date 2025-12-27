---
hide:
  - navigation
  - toc
---

<div class="hero-section">

<div class="hero-content">

<div style="text-align: center; margin-bottom: 1.5rem;">
  <img src="assets/CodeOptiX_Logo.png" alt="CodeOptiX Logo" class="hero-logo">
</div>

<h1 class="hero-title" style="font-size: 7rem !important; font-weight: 900 !important; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important;">CodeOptiX</h1>

<p class="hero-tagline">Agentic Code Optimization & Deep Evaluation for Superior Coding Agent Experience</p>

<p class="hero-description" style="font-size: 0.9rem; opacity: 0.8;">
<em>Built by <a href="https://super-agentic.ai" target="_blank"><strong>Superagentic AI</strong></a>, Powered by <a href="https://github.com/gepa-ai/gepa" target="_blank">GEPA</a> and <a href="https://github.com/safety-research/bloom" target="_blank">Bloom</a></em>
</p>

<div class="hero-buttons">
<a href="getting-started/installation/" class="md-button md-button--primary">
<span class="twemoji">🚀</span> Get Started
</a>
<a href="getting-started/quickstart/" class="md-button">
<span class="twemoji">⚡</span> Quick Start
</a>
<a href="https://github.com/SuperagenticAI/codeoptix" class="md-button" target="_blank">
<span class="twemoji">📦</span> View on GitHub
</a>
</div>

</div>

</div>

---

## 🔍 What is CodeOptiX?

**CodeOptiX is the universal code optimization engine that improves coding agent experience with deep evaluations and optimization.**

When AI coding agents dazzle with impressive code but leave you wondering about quality, maintainability, security, and reliability, CodeOptiX ensures proper behavior through evaluations, reflection, and self-improvement. Powered by [GEPA optimization](https://github.com/gepa-ai/gepa) and [Bloom scenario generation](https://github.com/safety-research/bloom).

### 🚀 Key Capabilities

- 🔍 **Deep Behavioral Evaluation** - Comprehensive testing against security, reliability, and quality behaviors
- 🧬 **GEPA Optimization Engine** - [Genetic-Pareto Evolution](https://github.com/gepa-ai/gepa) for automatic agent improvement
- 🌸 **Bloom-Style Scenario Generation** - [Intelligent test case creation](https://github.com/safety-research/bloom) for thorough evaluation
- 🎯 **Multi-Agent Support** - Works with Claude Code, Codex, Gemini CLI, and custom agents
- 🔧 **Multi-Provider LLM Support** - OpenAI, Anthropic, Google, and Ollama (local models included!)
- ⚡ **CI/CD Integration** - Automated quality gates and GitHub Actions support

!!! tip "Ollama Support - No API Key Required!"
    **CodeOptiX supports Ollama** for evaluations - use local models without API keys:

    - ✅ **Ollama integration** - Run evaluations with local models
    - ✅ **No API key needed** - Perfect for open-source users
    - ✅ **Privacy-friendly** - All processing happens locally
    - ✅ **Free to use** - No cloud costs
    - ⚠️ **Limited evolution support** - Use cloud providers for `codeoptix evolve`

    **See [Ollama Integration](guides/ollama-integration/) for setup and limitations.**

    **Cloud providers** (OpenAI, Anthropic, Google) still require API keys. See [Installation](getting-started/installation/#setting-up-llm-providers) for setup.

### 📋 Open Source Limitations

The open source version provides core evaluation capabilities. Advanced features like agent evolution and optimization have limited support. For full optimization capabilities tailored to your needs, please get in touch.

---

## 🚀 Quick Start (30 Seconds)

```bash
# 1. Install
pip install codeoptix

# 2. Option A: Use Ollama (No API key!)
ollama serve
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider ollama

# 2. Option B: Use cloud provider (requires API key)
export OPENAI_API_KEY="your-key-here"
codeoptix eval \
  --agent basic \
  --behaviors insecure-code \
  --llm-provider openai
```

**That's it!** You've just run your first quality check.

---

## ✨ Key Features

<div class="feature-grid">

<div class="feature-card">

<h3>🤖 Agent-Agnostic</h3>

<p>Works with <strong>any</strong> coding agent:</p>

<ul>
<li>Claude Code</li>
<li>Codex (GPT-5.2)</li>
<li>Gemini CLI</li>
<li>ACP-compatible agents</li>
<li>Custom agents</li>
</ul>

</div>

<div class="feature-card">

<h3>🎯 Behavior-Agnostic</h3>

<p>Modular behavior specifications:</p>

<ul>
<li><strong>insecure-code</strong> - Security vulnerabilities</li>
<li><strong>vacuous-tests</strong> - Test quality</li>
<li><strong>plan-drift</strong> - Requirements alignment</li>
<li>Custom behaviors</li>
</ul>

</div>

<div class="feature-card">

<h3>🔄 Self-Improving</h3>

<p>Evolves agent prompts using <strong>GEPA (Genetic-Pareto)</strong>:</p>

<ul>
<li>Automatic optimization</li>
<li>Iterative improvement</li>
<li>Performance tracking</li>
<li>Reflective mutation</li>
</ul>

</div>

<div class="feature-card">

<h3>📊 Deep Evaluations</h3>

<p>Comprehensive behavioral analysis:</p>

<ul>
<li>Multi-modal evaluation (static analysis, LLM, tests)</li>
<li>Bloom-style scenario generation</li>
<li>Root cause analysis</li>
<li>Actionable insights</li>
</ul>

</div>

<div class="feature-card">

<h3>🔌 Multiple Usage Modes</h3>

<p>Use CodeOptiX how you want:</p>

<ul>
<li><strong>Local Check</strong> - Run when ready to test</li>
<li><strong>CI/CD Mode</strong> - Automated quality gates</li>
<li><strong>ACP Integration</strong> - Editor quality bridge</li>
<li><strong>Standalone API</strong> - Programmatic access</li>
</ul>

</div>

<div class="feature-card">

<h3>📈 Reproducible</h3>

<p>All evaluations are versioned:</p>

<ul>
<li>Results tracking</li>
<li>Reflection reports</li>
<li>Evolution history</li>
<li>Artifact management</li>
</ul>

</div>

</div>

---

## 👥 Who Uses CodeOptiX?

<div class="user-grid">

<div class="user-card">

<h3>👨‍💻 Solo Developers</h3>

<p><strong>Pain Point:</strong> "I generated code with Claude Code/Codex/Gemini. Should I ship it?"</p>

<p><strong>Solution:</strong></p>
<ul>
<li>Quick quality checks after feature completion</li>
<li>Security scanning</li>
<li>Test quality validation</li>
<li>Multi-LLM critique</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix eval --agent claude-code --behaviors insecure-code
</code></pre>

</div>

<div class="user-card">

<h3>👥 Engineering Teams</h3>

<p><strong>Pain Point:</strong> "We need consistent quality gates for AI-generated code"</p>

<p><strong>Solution:</strong></p>
<ul>
<li>Automated CI/CD quality gates</li>
<li>PR-level quality enforcement</li>
<li>Team-wide standards</li>
<li>Behavioral optimization at scale</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix ci --agent codex --behaviors insecure-code --fail-on-failure
</code></pre>

</div>

<div class="user-card">

<h3>🔒 Security & Testing Teams</h3>

<p><strong>Pain Point:</strong> "We need automated security and behavior validation"</p>

<p><strong>Solution:</strong></p>
<ul>
<li>Automated security scanning</li>
<li>Behavior testing and validation</li>
<li>Agent optimization</li>
<li>Evaluation metrics and reporting</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix ci \
  --agent claude-code \
  --behaviors insecure-code,vacuous-tests \
  --config .codeoptix/config.yaml
</code></pre>

</div>

</div>

---

## 🏗️ How It Works

CodeOptiX follows a simple **Observe → Evaluate → Reflect → Evolve** workflow:

<div class="workflow-diagram">

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Observe   │ --> │  Evaluate   │ --> │  Reflect    │ --> │   Evolve    │
│             │     │             │     │             │     │             │
│ Capture     │     │ Measure     │     │ Generate    │     │ Optimize    │
│ agent       │     │ against     │     │ insights    │     │ prompts     │
│ behavior    │     │ behaviors   │     │ on failures │     │ with GEPA   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

</div>

### 1. **Observe**
Capture agent behavior (code, tests, traces) from any coding agent.

### 2. **Evaluate**
Measure behavior against configurable specifications (security, test quality, plan alignment).

### 3. **Reflect**
Generate actionable insights on failures with root cause analysis.

### 4. **Evolve**
Optimize agent prompts using GEPA (Genetic-Pareto) for continuous improvement.

---

## 🚀 Usage Modes

### Mode 1: Local Check (Primary)

**When:** You're ready to test your code after completing a feature/task

```bash
# Single behavior (recommended for getting started)
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --llm-provider openai

# Multiple behaviors
codeoptix eval \
  --agent codex \
  --behaviors insecure-code,vacuous-tests,plan-drift \
  --config examples/configs/basic.yaml
```

**Features:**

- ✅ Regression testing
- ✅ Code quality evaluation
- ✅ Multi-LLM critique (optional different model judge)
- ✅ Security scanning
- ✅ Optimization suggestions

### Mode 2: CI/CD Integration (Primary)

**When:** Teams want automated quality gates

```bash
# CI/CD optimized command
codeoptix ci \
  --agent codex \
  --behaviors insecure-code \
  --fail-on-failure \
  --output-format summary
```

**Features:**

- ✅ GitHub Actions integration
- ✅ Proper exit codes for automation
- ✅ Summary and JSON output formats
- ✅ Fail-fast behavior
- ✅ PR comments (coming soon)

### Mode 3: ACP Integration (Quality Bridge)

**When:** Users want quality checks integrated into editor workflow

```bash
# Register CodeOptiX as ACP agent
codeoptix acp register

# Use as quality bridge
codeoptix acp bridge --agent-name claude-code --auto-eval

# Multi-agent judge
codeoptix acp judge \
  --generate-agent claude-code \
  --judge-agent grok \
  --prompt "Write secure code"
```

**Features:**

- ✅ Quality bridge for editors (Zed, JetBrains, Neovim, VS Code)
- ✅ Multi-agent judge (generate with one, judge with another)
- ✅ Intelligent agent orchestration
- ✅ Real-time quality feedback
- ✅ Automatic code extraction

---

## 📋 Built-in Behaviors

CodeOptiX includes three built-in behavior specifications:

<div class="behavior-grid">

<div class="behavior-card">

<h3>🔒 insecure-code</h3>

<p><strong>Detects security vulnerabilities:</strong></p>

<ul>
<li>Hardcoded secrets</li>
<li>SQL injection risks</li>
<li>XSS vulnerabilities</li>
<li>Insecure authentication</li>
<li>And more...</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix eval --behaviors insecure-code
</code></pre>

</div>

<div class="behavior-card">

<h3>🧪 vacuous-tests</h3>

<p><strong>Identifies low-quality tests:</strong></p>

<ul>
<li>Missing assertions</li>
<li>Trivial tests</li>
<li>Test coverage issues</li>
<li>Meaningless test cases</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix eval --behaviors vacuous-tests
</code></pre>

</div>

<div class="behavior-card">

<h3>📐 plan-drift</h3>

<p><strong>Detects requirements misalignment:</strong></p>

<ul>
<li>Plan deviations</li>
<li>Missing features</li>
<li>Extra features</li>
<li>Requirements drift</li>
</ul>

<p><strong>Usage:</strong></p>
<pre><code>codeoptix eval --behaviors plan-drift --context plan.json
</code></pre>

</div>

</div>

---

## 💡 Example Use Cases

### Security Auditing

Ensure your agent never writes insecure code:

```bash
codeoptix eval \
  --agent claude-code \
  --behaviors insecure-code \
  --fail-on-failure
```

### Test Quality Validation

Verify your agent generates meaningful tests:

```bash
codeoptix eval \
  --agent codex \
  --behaviors vacuous-tests \
  --config examples/configs/single-behavior-vacuous-tests.yaml
```

### Requirements Alignment

Check that your agent follows requirements:

```bash
codeoptix eval \
  --agent gemini-cli \
  --behaviors plan-drift \
  --context requirements.json
```

### CI/CD Quality Gates

Automated quality checks in your pipeline:

```bash
codeoptix ci \
  --agent codex \
  --behaviors insecure-code,vacuous-tests \
  --fail-on-failure \
  --output-format summary
```

---

## 📦 Installation

### Using pip

```bash
pip install codeoptix
```

### Using uv (Recommended)

```bash
uv pip install codeoptix
```

### From Source

```bash
git clone https://github.com/SuperagenticAI/codeoptix.git
cd codeoptix
pip install -e .
```

---

## 📚 Documentation

### Getting Started

- [Installation](getting-started/installation.md) - Set up CodeOptiX
- [Quick Start](getting-started/quickstart.md) - Your first evaluation (free with Ollama!)
- [Single Behavior Quickstart](getting-started/single-behavior-quickstart.md) - Simple API key-based testing
- [Your First Evaluation](getting-started/first-evaluation.md) - Step-by-step guide

### Core Concepts

- [Overview](concepts/overview.md) - Understanding CodeOptiX
- [Agent Adapters](concepts/adapters.md) - Connecting to agents
- [Behavior Specifications](concepts/behaviors.md) - Defining behaviors
- [Evaluation Engine](concepts/evaluation.md) - Running evaluations
- [Reflection Engine](concepts/reflection.md) - Understanding results
- [Evolution Engine](concepts/evolution.md) - Improving agents
- [ACP Integration](concepts/acp.md) - Editor integration

### Guides

- [CLI Usage](guides/cli-usage.md) - Command-line interface (including `ci` command)
- [Python API](guides/python-api.md) - Use CodeOptiX in Python
- [Configuration](guides/configuration.md) - Advanced configuration
- [GitHub Actions](guides/github-actions.md) - CI/CD integration
- [ACP Integration](guides/acp-integration.md) - ACP protocol integration
- [Custom Behaviors](guides/custom-behaviors.md) - Create custom behaviors

### Advanced

- [GEPA Integration](advanced/gepa.md) - Genetic-Pareto optimization
- [Bloom Integration](advanced/bloom.md) - Scenario generation
- [Error Handling](advanced/error-handling.md) - Handle errors gracefully

---

## 🎓 Example Configurations

We provide ready-to-use configuration files:

- **`examples/configs/single-behavior-insecure-code.yaml`** - Security checks only
- **`examples/configs/single-behavior-vacuous-tests.yaml`** - Test quality only
- **`examples/configs/single-behavior-plan-drift.yaml`** - Requirements alignment only
- **`examples/configs/ci-cd.yaml`** - Optimized for CI/CD pipelines
- **`examples/configs/basic.yaml`** - Minimal configuration

See `examples/configs/` directory in the repository for configuration examples.

---

## 🏆 Why CodeOptiX?

<div class="why-grid">

<div class="why-card">

<h3>🎯 Agentic Code Optimizer</h3>

<p>CodeOptiX acts as your <strong>Agentic Code Optimizer</strong> - automatically evaluating, testing, and optimizing code generated by any coding agent using GEPA and Bloom.</p>

</div>

<div class="why-card">

<h3>🔄 When You're Ready</h3>

<p>Run CodeOptiX <strong>when you're ready to test</strong> - after completing a feature or task. No need to integrate into every step.</p>

</div>

<div class="why-card">

<h3>🤝 Works with Any Agent</h3>

<p>Don't lock yourself into one agent. CodeOptiX works with Claude Code, Codex, Gemini CLI, and any ACP-compatible agent.</p>

</div>

<div class="why-card">

<h3>📈 Continuous Improvement</h3>

<p>Evolve your agent prompts automatically using GEPA (Genetic-Pareto) for better results over time.</p>

</div>

</div>

---

## 🚀 Get Started Now

<div class="cta-section">

<h2>Ready to elevate your agent experience?</h2>

<div class="cta-buttons">

<a href="getting-started/installation/" class="md-button md-button--primary">
<span class="twemoji">🚀</span> Get Started
</a>

<a href="getting-started/quickstart/" class="md-button md-button--primary">
<span class="twemoji">⚡</span> Quick Start
</a>

<a href="https://github.com/SuperagenticAI/codeoptix/tree/main/examples" class="md-button" target="_blank">
<span class="twemoji">📦</span> View Examples
</a>

</div>

</div>

---

## 📞 Support & Community

- 📖 [Documentation](https://superagenticai.github.io/codeoptix)
- 💬 [GitHub Issues](https://github.com/SuperagenticAI/codeoptix/issues)
- 💬 [GitHub Discussions](https://github.com/SuperagenticAI/codeoptix/discussions)

---

## 📄 License

Apache License 2.0. See [LICENSE](https://github.com/SuperagenticAI/codeoptix/blob/main/LICENSE) for details.

---

## 🤖 About Superagentic AI

**CodeOptiX is proudly built by [Superagentic AI](https://super-agentic.ai)** - *Advancing the future of AI agent optimization and autonomous systems.*

### Our Mission
We're pioneering intelligent agent optimization technologies to enhance developer productivity and code quality. CodeOptiX represents our commitment to building tools that make AI coding assistants more reliable, efficient, and trustworthy.

### Explore More
- **[Visit Superagentic AI](https://super-agentic.ai)** - Learn about our mission and vision
- **[Our GitHub](https://github.com/SuperagenticAI)** - Discover our other AI agent projects

---

<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: var(--md-default-bg-color--lighter); border-radius: 8px;">
<p><strong>Brought to you by <a href="https://super-agentic.ai" target="_blank">Superagentic AI</a></strong></p>
<p><a href="https://github.com/SuperagenticAI/codeoptix" class="md-button">⭐ Star us on GitHub</a></p>
</div>
