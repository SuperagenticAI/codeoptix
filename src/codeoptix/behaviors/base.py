"""Base behavior specification interface for CodeFlect."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class Severity(str, Enum):
    """Severity levels for behavior violations."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BehaviorResult:
    """Result of behavior evaluation."""
    
    behavior_name: str
    passed: bool
    score: float  # 0.0 to 1.0 (1.0 = perfect, 0.0 = failed)
    evidence: List[str] = field(default_factory=list)
    severity: Severity = Severity.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate score range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")


class BehaviorSpec(ABC):
    """Base interface for behavior specifications."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize behavior spec with configuration.
        
        Args:
            config: Behavior-specific configuration dictionary
        """
        self.config = config or {}
        self.name = self.get_name()
        self.severity = Severity(self.config.get("severity", "medium"))
        self.enabled = self.config.get("enabled", True)
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name identifier for this behavior."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of behavior."""
        pass
    
    @abstractmethod
    def evaluate(
        self,
        agent_output: Any,  # AgentOutput from adapters
        context: Optional[Dict[str, Any]] = None
    ) -> BehaviorResult:
        """
        Evaluate agent output against behavior spec.
        
        Args:
            agent_output: Output from agent adapter (AgentOutput)
            context: Optional context (files, workspace, planning artifacts, etc.)
            
        Returns:
            BehaviorResult with evaluation results
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if this behavior spec is enabled."""
        return self.enabled
    
    def get_severity(self) -> Severity:
        """Get the severity level for this behavior."""
        return self.severity

