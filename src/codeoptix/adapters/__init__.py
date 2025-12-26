"""Agent adapters for CodeOptix."""

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.adapters.basic import BasicAdapter
from codeoptix.adapters.claude_code import ClaudeCodeAdapter
from codeoptix.adapters.codex import CodexAdapter
from codeoptix.adapters.factory import create_adapter
from codeoptix.adapters.gemini_cli import GeminiCLIAdapter

__all__ = [
    "AgentAdapter",
    "AgentOutput",
    "BasicAdapter",
    "ClaudeCodeAdapter",
    "CodexAdapter",
    "GeminiCLIAdapter",
    "create_adapter",
]
