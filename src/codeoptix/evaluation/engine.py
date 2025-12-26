"""Evaluation engine for CodeOptix."""

from typing import Any

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.behaviors import BehaviorSpec, create_behavior
from codeoptix.evaluation.evaluators import (
    ArtifactComparator,
    LLMEvaluator,
    StaticAnalyzer,
    TestRunner,
)
from codeoptix.evaluation.scenario_generator import BloomScenarioGenerator, ScenarioGenerator
from codeoptix.utils.llm import LLMClient


class EvaluationEngine:
    """
    Main evaluation engine that orchestrates behavior evaluation.

    Supports:
    - Bloom-style scenario generation
    - Multi-modal evaluation (static analysis, LLM, tests)
    - Custom scenario generators
    """

    def __init__(
        self, adapter: AgentAdapter, llm_client: LLMClient, config: dict[str, Any] | None = None
    ):
        """
        Initialize evaluation engine.

        Args:
            adapter: Agent adapter for executing tasks
            llm_client: LLM client for evaluation and scenario generation
            config: Configuration dictionary
        """
        self.adapter = adapter
        self.llm_client = llm_client
        self.config = config or {}

        # Initialize evaluators
        self.static_analyzer = StaticAnalyzer(self.config.get("static_analysis", {}))
        self.test_runner = TestRunner(self.config.get("test_runner", {}))
        self.llm_evaluator = LLMEvaluator(llm_client, self.config.get("llm_evaluator", {}))
        self.artifact_comparator = ArtifactComparator(self.config.get("artifact_comparator", {}))

        # Initialize scenario generator
        scenario_config = self.config.get("scenario_generator", {})
        use_bloom = scenario_config.get("use_bloom", True)

        if use_bloom:
            self.scenario_generator = BloomScenarioGenerator(llm_client, scenario_config)
        else:
            self.scenario_generator = ScenarioGenerator(llm_client, scenario_config)

    def evaluate_behaviors(
        self,
        behavior_names: list[str],
        scenarios: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate agent against multiple behaviors.

        Args:
            behavior_names: List of behavior names to evaluate
            scenarios: Optional pre-generated scenarios
            context: Optional context (planning artifacts, etc.)

        Returns:
            Dictionary with evaluation results
        """
        context = context or {}
        results = {
            "behaviors": {},
            "scenarios": scenarios or [],
            "overall_score": 0.0,
            "metadata": {},
        }

        # Generate scenarios if not provided
        if not scenarios:
            scenarios = self._generate_scenarios_for_behaviors(behavior_names)
            results["scenarios"] = scenarios

        # Validate behavior names (keep list in sync with BEHAVIOR_REGISTRY)
        valid_behaviors = [
            "insecure-code",
            "vacuous-tests",
            "plan-drift",
        ]
        invalid_behaviors = [b for b in behavior_names if b not in valid_behaviors]
        if invalid_behaviors:
            raise ValueError(
                f"Invalid behavior name(s): {', '.join(invalid_behaviors)}. "
                f"Available behaviors: {', '.join(valid_behaviors)}"
            )

        if not behavior_names:
            raise ValueError("At least one behavior must be specified")

        # Evaluate each behavior
        behavior_results = {}
        enabled_behaviors = []
        for behavior_name in behavior_names:
            try:
                behavior = create_behavior(
                    behavior_name, self.config.get("behaviors", {}).get(behavior_name, {})
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to create behavior '{behavior_name}': {e}. "
                    f"Please check the behavior name and configuration."
                ) from e

            if not behavior.is_enabled():
                continue

            enabled_behaviors.append(behavior_name)

            # Get scenarios for this behavior
            behavior_scenarios = [s for s in scenarios if s.get("behavior") == behavior_name]

            # Run evaluation
            behavior_result = self._evaluate_behavior(
                behavior=behavior, scenarios=behavior_scenarios, context=context
            )

            behavior_results[behavior_name] = behavior_result

        if not enabled_behaviors:
            raise ValueError(
                "No enabled behaviors found. "
                "Please ensure at least one behavior is enabled in the configuration."
            )

        results["behaviors"] = behavior_results

        # Calculate overall score
        if behavior_results:
            scores = [r["score"] for r in behavior_results.values()]
            results["overall_score"] = sum(scores) / len(scores)

        return results

    def _generate_scenarios_for_behaviors(self, behavior_names: list[str]) -> list[dict[str, Any]]:
        """Generate scenarios for all behaviors."""
        all_scenarios = []

        for behavior_name in behavior_names:
            behavior = create_behavior(behavior_name)
            behavior_description = behavior.get_description()

            # Generate scenarios for this behavior
            scenarios = self.scenario_generator.generate_scenarios(
                behavior_name=behavior_name, behavior_description=behavior_description
            )

            # Tag scenarios with behavior name
            for scenario in scenarios:
                scenario["behavior"] = behavior_name

            all_scenarios.extend(scenarios)

        return all_scenarios

    def _evaluate_behavior(
        self, behavior: BehaviorSpec, scenarios: list[dict[str, Any]], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate a single behavior across scenarios.

        Args:
            behavior: Behavior spec to evaluate
            scenarios: Scenarios to test
            context: Evaluation context

        Returns:
            Dictionary with behavior evaluation results
        """
        if not scenarios:
            # Generate default scenario
            scenarios = [
                {
                    "task": f"Test {behavior.get_name()}",
                    "prompt": f"Write code that should be evaluated for: {behavior.get_description()}",
                    "behavior": behavior.get_name(),
                }
            ]

        scenario_results = []
        all_evidence = []
        scores = []

        for scenario in scenarios:
            # Execute agent with scenario prompt
            prompt = scenario.get("prompt", "")
            agent_output = self.adapter.execute(prompt, context=context)

            # Run behavior evaluation
            behavior_result = behavior.evaluate(agent_output, context=context)

            # Run additional evaluators
            evaluator_results = self._run_evaluators(agent_output, behavior, context)

            # Combine results
            scenario_result = {
                "scenario": scenario,
                "behavior_result": {
                    "passed": behavior_result.passed,
                    "score": behavior_result.score,
                    "severity": behavior_result.severity.value,
                    "evidence": behavior_result.evidence,
                },
                "evaluator_results": evaluator_results,
                "agent_output": {
                    "code_length": len(agent_output.code or ""),
                    "has_tests": bool(agent_output.tests),
                },
            }

            scenario_results.append(scenario_result)
            all_evidence.extend(behavior_result.evidence)
            scores.append(behavior_result.score)

        # Aggregate results
        avg_score = sum(scores) / len(scores) if scores else 0.0
        passed_count = sum(1 for r in scenario_results if r["behavior_result"]["passed"])

        return {
            "behavior_name": behavior.get_name(),
            "scenarios_tested": len(scenarios),
            "scenarios_passed": passed_count,
            "score": avg_score,
            "evidence": all_evidence,
            "scenario_results": scenario_results,
            "metadata": {
                "total_evidence_items": len(all_evidence),
                "min_score": min(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
            },
        }

    def _run_evaluators(
        self, agent_output: AgentOutput, behavior: BehaviorSpec, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Run additional evaluators (static analysis, tests, LLM)."""
        results = {}

        code = agent_output.code or ""
        tests = agent_output.tests or ""

        # Static analysis
        if code:
            results["static_analysis"] = self.static_analyzer.analyze(code)

        # Test execution
        if code and tests:
            results["test_execution"] = self.test_runner.run_tests(code, tests)

        # LLM evaluation
        if code:
            results["llm_evaluation"] = self.llm_evaluator.evaluate(
                code=code, behavior_description=behavior.get_description(), context=context
            )

        # Artifact comparison
        if context.get("plan") or context.get("requirements"):
            results["artifact_comparison"] = self.artifact_comparator.compare(
                code=code, artifacts=context
            )

        return results
