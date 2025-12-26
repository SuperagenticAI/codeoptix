"""Factory for creating agent adapters."""

from typing import Any

from codeoptix.adapters.base import AgentAdapter
from codeoptix.adapters.basic import BasicAdapter
from codeoptix.adapters.claude_code import ClaudeCodeAdapter
from codeoptix.adapters.codex import CodexAdapter
from codeoptix.adapters.gemini_cli import GeminiCLIAdapter


def create_adapter(adapter_type: str, config: dict[str, Any]) -> AgentAdapter:
    """
    Factory function to create an agent adapter.

    Args:
        adapter_type: Type of adapter ("basic", "claude-code", "codex", "gemini-cli")
        config: Configuration dictionary for the adapter

    Returns:
        AgentAdapter instance

    Raises:
        ValueError: If adapter_type is not supported
    """
    adapter_map = {
        "basic": BasicAdapter,
        "claude-code": ClaudeCodeAdapter,
        "codex": CodexAdapter,
        "gemini-cli": GeminiCLIAdapter,
    }

    adapter_class = adapter_map.get(adapter_type)
    if adapter_class is None:
        supported = ", ".join(adapter_map.keys())
        raise ValueError(
            f"Unsupported adapter type: '{adapter_type}'. "
            f"Supported types: {supported}. "
            f"For testing without external agents, use 'basic'."
        )

    try:
        return adapter_class(config)
    except KeyError as e:
        if "api_key" in str(e) or "llm_config" in str(e):
            raise ValueError(
                f"Missing required configuration for {adapter_type}. "
                f"Please provide 'llm_config' with 'api_key' in the adapter configuration. "
                f"Example: {{'llm_config': {{'provider': 'openai', 'api_key': 'your-key'}}}}"
            ) from e
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to initialize {adapter_type} adapter: {e}. "
            f"Please check your configuration and API keys."
        ) from e
