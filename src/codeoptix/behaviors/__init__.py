"""Behavior specifications for CodeOptix."""

from codeoptix.behaviors.base import BehaviorResult, BehaviorSpec, Severity
from codeoptix.behaviors.insecure_code import InsecureCodeBehavior
from codeoptix.behaviors.plan_drift import PlanDriftBehavior
from codeoptix.behaviors.vacuous_tests import VacuousTestsBehavior

__all__ = [
    "BehaviorResult",
    "BehaviorSpec",
    "InsecureCodeBehavior",
    "PlanDriftBehavior",
    "Severity",
    "VacuousTestsBehavior",
]

# Registry of available behaviors
BEHAVIOR_REGISTRY = {
    "insecure-code": InsecureCodeBehavior,
    "vacuous-tests": VacuousTestsBehavior,
    "plan-drift": PlanDriftBehavior,
}


def create_behavior(name: str, config: dict | None = None) -> BehaviorSpec:
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
            f"Unknown behavior: {name}. Available behaviors: {', '.join(BEHAVIOR_REGISTRY.keys())}"
        )

    behavior_class = BEHAVIOR_REGISTRY[name]
    return behavior_class(config=config or {})
