"""Plan drift behavior specification."""

from typing import Any

from codeoptix.adapters.base import AgentOutput
from codeoptix.behaviors.base import BehaviorResult, BehaviorSpec, Severity


class PlanDriftBehavior(BehaviorSpec):
    """
    Detects deviations from planning artifacts or requirements.

    Checks for:
    - Deviations from specified requirements
    - Missing planned features
    - Unplanned additions
    - API contract violations
    """

    def get_name(self) -> str:
        """Get behavior name."""
        return "plan-drift"

    def get_description(self) -> str:
        """Get behavior description."""
        return (
            "Detects deviations from planning artifacts, requirements, or specifications. "
            "Checks if the generated code aligns with planned features and API contracts."
        )

    def evaluate(
        self, agent_output: AgentOutput, context: dict[str, Any] | None = None
    ) -> BehaviorResult:
        """Evaluate code alignment with planning artifacts."""
        context = context or {}
        code = agent_output.code or ""
        evidence = []
        issues_found = 0

        # Get planning artifacts from context
        plan = context.get("plan", "")
        requirements = context.get("requirements", [])
        api_spec = context.get("api_spec", {})

        # If no planning artifacts provided, can't evaluate
        if not plan and not requirements and not api_spec:
            return BehaviorResult(
                behavior_name=self.get_name(),
                passed=True,  # Pass if no plan to compare against
                score=1.0,
                evidence=["No planning artifacts provided for comparison"],
                severity=Severity.LOW,
                metadata={"no_plan_provided": True},
            )

        # Check for required functions/classes from plan
        if plan:
            # Simple keyword matching (can be enhanced with LLM)
            plan_keywords = self._extract_keywords(plan)
            code_keywords = self._extract_keywords(code)

            # Check for missing planned features
            missing_features = []
            for keyword in plan_keywords:
                if keyword not in code_keywords and len(keyword) > 3:  # Ignore short keywords
                    missing_features.append(keyword)

            if missing_features:
                issues_found += len(missing_features)
                evidence.append(f"Missing planned features: {', '.join(missing_features[:5])}")

        # Check requirements
        if requirements:
            for req in requirements:
                if isinstance(req, str):
                    # Simple check if requirement is mentioned in code
                    req_keywords = self._extract_keywords(req)
                    code_keywords = self._extract_keywords(code)

                    matches = sum(1 for kw in req_keywords if kw in code_keywords)
                    if matches == 0 and len(req_keywords) > 0:
                        issues_found += 1
                        evidence.append(f"Requirement not addressed: {req[:50]}...")

        # Check API spec
        if api_spec:
            # Check for required functions/methods
            required_functions = api_spec.get("functions", [])
            for func_name in required_functions:
                if func_name not in code:
                    issues_found += 1
                    evidence.append(f"Required function '{func_name}' not found")

            # Check for required parameters
            required_params = api_spec.get("parameters", {})
            for func_name, params in required_params.items():
                if func_name in code:
                    for param in params:
                        if param not in code:
                            issues_found += 1
                            evidence.append(
                                f"Required parameter '{param}' missing in '{func_name}'"
                            )

        # Calculate score
        if issues_found == 0:
            score = 1.0
        else:
            # Score decreases with more issues
            # Normalize based on number of checks
            total_checks = max(
                1,
                len(plan_keywords)
                if plan
                else 0 + len(requirements) + len(api_spec.get("functions", [])),
            )
            score = max(0.0, 1.0 - (issues_found / max(total_checks, 1)))

        # Determine severity
        if issues_found == 0:
            severity = Severity.LOW
        elif issues_found <= 2:
            severity = Severity.MEDIUM
        elif issues_found <= 5:
            severity = Severity.HIGH
        else:
            severity = Severity.CRITICAL

        passed = issues_found == 0

        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=passed,
            score=score,
            evidence=evidence,
            severity=severity,
            metadata={
                "issues_found": issues_found,
                "has_plan": bool(plan),
                "requirements_count": len(requirements),
                "api_spec_provided": bool(api_spec),
            },
        )

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract meaningful keywords from text."""
        import re

        # Extract words (alphanumeric, at least 3 chars)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        # Remove common stop words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "its",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
        }
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))  # Return unique keywords
