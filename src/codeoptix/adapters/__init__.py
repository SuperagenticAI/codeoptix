"""Agent adapters for CodeFlect."""

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.adapters.claude_code import ClaudeCodeAdapter
from codeoptix.adapters.codex import CodexAdapter
from codeoptix.adapters.gemini_cli import GeminiCLIAdapter
from codeoptix.adapters.factory import create_adapter

__all__ = [
    "AgentAdapter",
    "AgentOutput",
    "ClaudeCodeAdapter",
    "CodexAdapter",
    "GeminiCLIAdapter",
    "create_adapter",
]

