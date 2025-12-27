# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.3] - 2025-12-27

### Added
- Ollama integration demo script (`examples/ollama_demo.py`) showcasing working local evaluations
- Updated documentation highlighting Ollama integration fixes

### Fixed
- **Ollama Integration**: Fixed Ollama models to properly generate code and provide meaningful evaluation scores instead of always returning 100%. Now uses Ollama's chat API for better conversation handling and includes working demo script.

## [0.1.2] - 2025-12-26

### Added
- Initial release of CodeOptiX
- GEPA optimization engine
- Bloom evaluation framework
- Built-in behaviors: insecure-code, vacuous-tests, plan-drift
- Support for multiple coding agents (Claude Code, Codex, Gemini CLI)
- Multi-provider LLM support (OpenAI, Anthropic, Google, Ollama)
- CI/CD integration
- Comprehensive documentation and examples

## [0.1.0] - 2025-12-26

### Added
- Project initialization
