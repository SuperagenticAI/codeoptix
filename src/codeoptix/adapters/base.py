"""Base adapter interface for coding agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AgentOutput:
    """Standardized output from any coding agent."""
    
    code: str
    tests: Optional[str] = None
    traces: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    prompt_used: Optional[str] = None


class AgentAdapter(ABC):
    """Base interface for agent adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize adapter with configuration."""
        self.config = config
        self._current_prompt: Optional[str] = None
    
    @abstractmethod
    def execute(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute agent with prompt and return standardized output.
        
        Args:
            prompt: The task prompt for the agent
            context: Optional context (files, workspace info, etc.)
            
        Returns:
            AgentOutput with code, tests, traces, and metadata
        """
        pass
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Get current agent prompt/policy."""
        pass
    
    @abstractmethod
    def update_prompt(self, new_prompt: str) -> None:
        """Update agent prompt/policy."""
        pass
    
    @abstractmethod
    def get_adapter_type(self) -> str:
        """Get the type identifier for this adapter."""
        pass

