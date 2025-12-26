"""Configuration management for CodeOptiX."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: str = Field(
        default="anthropic", description="LLM provider (anthropic, openai, google)"
    )
    model: str = Field(default="claude-opus-4-5-20251101", description="Model name")
    api_key: str | None = Field(default=None, description="API key (or use environment variable)")
    temperature: float = Field(default=1.0, description="Temperature for generation")
    max_tokens: int | None = Field(default=None, description="Max tokens")


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str = Field(description="Agent name")
    adapter_type: str = Field(description="Adapter type (claude-code, codex, gemini-cli)")
    llm_config: LLMConfig = Field(description="LLM configuration")
    prompt: str | None = Field(default=None, description="Agent prompt/policy")


class BehaviorConfig(BaseModel):
    """Behavior specification configuration."""

    name: str = Field(description="Behavior name")
    enabled: bool = Field(default=True, description="Whether behavior is enabled")
    severity: str = Field(default="medium", description="Severity level")
    config: dict[str, Any] = Field(default_factory=dict, description="Behavior-specific config")


class CodeOptixConfig(BaseModel):
    """Main CodeOptix configuration."""

    agent: AgentConfig = Field(description="Agent configuration")
    behaviors: list[BehaviorConfig] = Field(
        default_factory=list, description="Behavior specifications"
    )
    evaluation: dict[str, Any] = Field(default_factory=dict, description="Evaluation settings")
    reflection: dict[str, Any] = Field(default_factory=dict, description="Reflection settings")
    evolution: dict[str, Any] = Field(default_factory=dict, description="Evolution settings")
    artifacts_dir: str = Field(default=".codeoptix/artifacts", description="Artifacts directory")


def load_config(config_path: str | Path) -> CodeOptixConfig:
    """Load configuration from YAML file."""
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    # Load API keys from environment if not provided
    if "agent" in config_data and "llm_config" in config_data["agent"]:
        llm_config = config_data["agent"]["llm_config"]
        provider = llm_config.get("provider", "anthropic")

        if not llm_config.get("api_key"):
            # Try to get from environment
            env_key_map = {
                "anthropic": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "google": "GOOGLE_API_KEY",
            }
            env_key = env_key_map.get(provider)
            if env_key:
                api_key = os.getenv(env_key)
                if api_key:
                    llm_config["api_key"] = api_key

    return CodeOptixConfig(**config_data)


def save_config(config: CodeOptixConfig, config_path: str | Path) -> None:
    """Save configuration to YAML file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)
