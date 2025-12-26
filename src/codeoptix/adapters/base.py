"""Base adapter interface for coding agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentOutput:
    """Standardized output from any coding agent."""

    code: str
    tests: str | None = None
    traces: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    prompt_used: str | None = None


class AgentAdapter(ABC):
    """Base interface for agent adapters."""

    def __init__(self, config: dict[str, Any]):
        """Initialize adapter with configuration."""
        self.config = config
        self._current_prompt: str | None = None

    @abstractmethod
    def execute(self, prompt: str, context: dict[str, Any] | None = None) -> AgentOutput:
        """
        Execute agent with prompt and return standardized output.

        Args:
            prompt: The task prompt for the agent
            context: Optional context (files, workspace info, etc.)

        Returns:
            AgentOutput with code, tests, traces, and metadata
        """

    @abstractmethod
    def get_prompt(self) -> str:
        """Get current agent prompt/policy."""

    @abstractmethod
    def update_prompt(self, new_prompt: str) -> None:
        """Update agent prompt/policy."""

    @abstractmethod
    def get_adapter_type(self) -> str:
        """Get the type identifier for this adapter."""
