"""Behavior specifications for CodeFlect."""

from typing import Optional

from codeoptix.behaviors.base import BehaviorResult, BehaviorSpec, Severity
from codeoptix.behaviors.insecure_code import InsecureCodeBehavior
from codeoptix.behaviors.plan_drift import PlanDriftBehavior
from codeoptix.behaviors.vacuous_tests import VacuousTestsBehavior

__all__ = [
    "BehaviorSpec",
    "BehaviorResult",
    "Severity",
    "InsecureCodeBehavior",
    "VacuousTestsBehavior",
    "PlanDriftBehavior",
]

# Registry of available behaviors
BEHAVIOR_REGISTRY = {
    "insecure-code": InsecureCodeBehavior,
    "vacuous-tests": VacuousTestsBehavior,
    "plan-drift": PlanDriftBehavior,
}


def create_behavior(name: str, config: Optional[dict] = None) -> BehaviorSpec:
    """
    Factory function to create a behavior spec.
    
    Args:
        name: Behavior name (e.g., "insecure-code")
        config: Optional configuration dictionary
        
    Returns:
        BehaviorSpec instance
        
    Raises:
        ValueError: If behavior name is not found
    """
    if name not in BEHAVIOR_REGISTRY:
        raise ValueError(
            f"Unknown behavior: {name}. "
            f"Available behaviors: {', '.join(BEHAVIOR_REGISTRY.keys())}"
        )
    
    behavior_class = BEHAVIOR_REGISTRY[name]
    return behavior_class(config=config or {})
