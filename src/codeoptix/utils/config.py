"""Configuration management for CodeOptiX."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration."""
    
    provider: str = Field(default="anthropic", description="LLM provider (anthropic, openai, google)")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key (or use environment variable)")
    temperature: float = Field(default=1.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens")


class AgentConfig(BaseModel):
    """Agent configuration."""
    
    name: str = Field(description="Agent name")
    adapter_type: str = Field(description="Adapter type (claude-code, codex, gemini-cli)")
    llm_config: LLMConfig = Field(description="LLM configuration")
    prompt: Optional[str] = Field(default=None, description="Agent prompt/policy")


class BehaviorConfig(BaseModel):
    """Behavior specification configuration."""
    
    name: str = Field(description="Behavior name")
    enabled: bool = Field(default=True, description="Whether behavior is enabled")
    severity: str = Field(default="medium", description="Severity level")
    config: Dict[str, Any] = Field(default_factory=dict, description="Behavior-specific config")


class CodeFlectConfig(BaseModel):
    """Main CodeFlect configuration."""
    
    agent: AgentConfig = Field(description="Agent configuration")
    behaviors: list[BehaviorConfig] = Field(default_factory=list, description="Behavior specifications")
    evaluation: Dict[str, Any] = Field(default_factory=dict, description="Evaluation settings")
    reflection: Dict[str, Any] = Field(default_factory=dict, description="Reflection settings")
    evolution: Dict[str, Any] = Field(default_factory=dict, description="Evolution settings")
    artifacts_dir: str = Field(default=".codeflect/artifacts", description="Artifacts directory")


def load_config(config_path: str | Path) -> CodeFlectConfig:
    """Load configuration from YAML file."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
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
    
    return CodeFlectConfig(**config_data)


def save_config(config: CodeFlectConfig, config_path: str | Path) -> None:
    """Save configuration to YAML file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

