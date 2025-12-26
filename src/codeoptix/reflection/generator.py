"""Reflection content generation for CodeOptiX."""

from typing import Any


class ReflectionGenerator:
    """Generates human-readable reflection reports from evaluation results."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize reflection generator."""
        self.config = config or {}

    def generate(self, results: dict[str, Any], agent_name: str | None = None) -> str:
        """
        Generate reflection markdown from evaluation results.

        Args:
            results: Evaluation results dictionary
            agent_name: Optional agent name

        Returns:
            Reflection markdown content
        """
        run_id = results.get("run_id", "unknown")
        timestamp = results.get("timestamp", "unknown")
        overall_score = results.get("overall_score", 0.0)
        behaviors = results.get("behaviors", {})

        lines = []
        lines.append("# CodeOptiX Reflection Report\n")
        lines.append(f"**Run ID**: {run_id}  \n")
        lines.append(f"**Timestamp**: {timestamp}  \n")
        if agent_name:
            lines.append(f"**Agent**: {agent_name}  \n")
        lines.append(f"**Overall Score**: {overall_score:.2f}/1.0  \n")
        lines.append("\n---\n")

        # Summary section
        lines.append("## Summary\n\n")
        total_behaviors = len(behaviors)
        passed_behaviors = sum(1 for b in behaviors.values() if b.get("scenarios_passed", 0) > 0)
        failed_behaviors = total_behaviors - passed_behaviors

        lines.append(f"- **Total Behaviors Evaluated**: {total_behaviors}\n")
        lines.append(f"- **Behaviors Passed**: {passed_behaviors}\n")
        lines.append(f"- **Behaviors Failed**: {failed_behaviors}\n")
        lines.append(f"- **Overall Score**: {overall_score:.2f}/1.0\n")
        lines.append("\n")

        # Behavior analysis section
        lines.append("## Behavior Analysis\n\n")

        for behavior_name, behavior_data in behaviors.items():
            lines.append(f"### {behavior_name}\n\n")

            score = behavior_data.get("score", 0.0)
            scenarios_tested = behavior_data.get("scenarios_tested", 0)
            scenarios_passed = behavior_data.get("scenarios_passed", 0)
            scenario_results = behavior_data.get("scenario_results", [])
            severity = (
                scenario_results[0].get("behavior_result", {}).get("severity", "medium")
                if scenario_results
                else "medium"
            )
            evidence = behavior_data.get("evidence", [])

            # Status badge
            status = "✅ PASSED" if scenarios_passed > 0 else "❌ FAILED"
            lines.append(f"**Status**: {status}  \n")
            lines.append(f"**Score**: {score:.2f}/1.0  \n")
            lines.append(f"**Severity**: {severity.upper()}  \n")
            lines.append(f"**Scenarios Tested**: {scenarios_tested}  \n")
            lines.append(f"**Scenarios Passed**: {scenarios_passed}  \n")
            lines.append("\n")

            # Evidence
            if evidence:
                lines.append("**Evidence**:\n")
                for ev in evidence[:10]:  # Limit to 10 items
                    lines.append(f"- {ev}\n")
                if len(evidence) > 10:
                    lines.append(f"- ... and {len(evidence) - 10} more issues\n")
                lines.append("\n")

            # Root cause analysis
            root_causes = self._identify_root_causes(behavior_data)
            if root_causes:
                lines.append("**Root Causes**:\n")
                for cause in root_causes:
                    lines.append(f"- {cause}\n")
                lines.append("\n")

            # Recommendations
            recommendations = self._generate_recommendations(behavior_name, behavior_data)
            if recommendations:
                lines.append("**Recommendations**:\n")
                for rec in recommendations:
                    lines.append(f"- {rec}\n")
                lines.append("\n")

            lines.append("---\n\n")

        # Overall recommendations
        lines.append("## Overall Recommendations\n\n")
        overall_recs = self._generate_overall_recommendations(results)
        for rec in overall_recs:
            lines.append(f"- {rec}\n")
        lines.append("\n")

        # Metadata
        lines.append("## Metadata\n\n")
        metadata = results.get("metadata", {})
        for key, value in metadata.items():
            lines.append(f"- **{key}**: {value}\n")

        return "".join(lines)

    def _identify_root_causes(self, behavior_data: dict[str, Any]) -> list[str]:
        """Identify root causes from behavior evaluation."""
        causes = []

        evidence = behavior_data.get("evidence", [])
        scenario_results = behavior_data.get("scenario_results", [])

        # Analyze evidence patterns
        if any("hardcoded" in ev.lower() for ev in evidence):
            causes.append("Missing security guidelines in agent prompt")

        if any("no assertions" in ev.lower() for ev in evidence):
            causes.append("Insufficient test quality requirements in prompt")

        if any("missing" in ev.lower() for ev in evidence):
            causes.append("Agent not following planning artifacts")

        # Check evaluator results
        for scenario_result in scenario_results:
            eval_results = scenario_result.get("evaluator_results", {})

            if eval_results.get("static_analysis", {}).get("bandit"):
                bandit_data = eval_results["static_analysis"]["bandit"]
                if (
                    bandit_data
                    and bandit_data.get("metrics", {}).get("_totals", {}).get("SEVERITY.HIGH", 0)
                    > 0
                ):
                    causes.append("Static analysis detected security vulnerabilities")

            if eval_results.get("test_execution", {}).get("failed_count", 0) > 0:
                causes.append("Tests are failing or have low coverage")

        return list(set(causes))  # Remove duplicates

    def _generate_recommendations(
        self, behavior_name: str, behavior_data: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations for a specific behavior."""
        recommendations = []
        score = behavior_data.get("score", 0.0)
        evidence = behavior_data.get("evidence", [])

        if behavior_name == "insecure-code":
            if score < 0.7:
                recommendations.append("Add security checklist to agent prompt")
                recommendations.append("Include examples of secure code patterns")
                recommendations.append("Add explicit guidance against hardcoded secrets")

        elif behavior_name == "vacuous-tests":
            if score < 0.7:
                recommendations.append("Emphasize test quality requirements in prompt")
                recommendations.append("Include examples of meaningful test assertions")
                recommendations.append("Add guidance on test coverage expectations")

        elif behavior_name == "plan-drift":
            if score < 0.7:
                recommendations.append("Strengthen alignment with planning artifacts")
                recommendations.append("Add explicit requirement tracking in prompt")
                recommendations.append("Include examples of plan-following behavior")

        # General recommendations based on evidence
        if len(evidence) > 5:
            recommendations.append(
                "Multiple issues detected - consider comprehensive prompt revision"
            )

        return recommendations

    def _generate_overall_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate overall recommendations."""
        recommendations = []
        overall_score = results.get("overall_score", 0.0)
        behaviors = results.get("behaviors", {})

        if overall_score < 0.5:
            recommendations.append("**Critical**: Agent performance is below acceptable threshold")
            recommendations.append("Consider major prompt revision or agent configuration changes")
        elif overall_score < 0.7:
            recommendations.append("**Warning**: Agent performance needs improvement")
            recommendations.append("Review and update agent prompts based on evidence")
        else:
            recommendations.append("Agent performance is acceptable but can be improved")

        # Behavior-specific recommendations
        failed_behaviors = [
            name for name, data in behaviors.items() if data.get("score", 0.0) < 0.7
        ]
        if failed_behaviors:
            recommendations.append(f"Focus on improving: {', '.join(failed_behaviors)}")

        return recommendations
