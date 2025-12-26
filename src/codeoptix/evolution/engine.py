"""Evolution engine for CodeOptix using GEPA-style patterns."""

from typing import Any

from codeoptix.adapters.base import AgentAdapter
from codeoptix.artifacts.manager import ArtifactManager
from codeoptix.evaluation import EvaluationEngine
from codeoptix.evolution.proposer import PromptProposer
from codeoptix.utils.llm import LLMClient


class EvolutionEngine:
    """
    Evolution engine that optimizes agent prompts using GEPA-style reflective mutation.

    Uses evaluation results and reflection to evolve prompts iteratively.
    """

    def __init__(
        self,
        adapter: AgentAdapter,
        evaluation_engine: EvaluationEngine,
        llm_client: LLMClient,
        artifact_manager: ArtifactManager | None = None,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize evolution engine.

        Args:
            adapter: Agent adapter to evolve
            evaluation_engine: Evaluation engine for testing candidates
            llm_client: LLM client for prompt proposal
            artifact_manager: Artifact manager for saving evolved prompts
            config: Configuration dictionary
        """
        self.adapter = adapter
        self.evaluation_engine = evaluation_engine
        self.llm_client = llm_client
        self.artifact_manager = artifact_manager
        self.config = config or {}

        # Evolution parameters
        self.max_iterations = self.config.get("max_iterations", 3)
        self.population_size = self.config.get("population_size", 3)
        self.minibatch_size = self.config.get("minibatch_size", 2)
        self.improvement_threshold = self.config.get("improvement_threshold", 0.05)

        # Initialize proposer
        proposer_config = self.config.get("proposer", {})
        self.proposer = PromptProposer(llm_client, proposer_config)

    def evolve(
        self,
        evaluation_results: dict[str, Any],
        reflection: str,
        behavior_names: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evolve agent prompts based on evaluation results.

        Args:
            evaluation_results: Previous evaluation results
            reflection: Reflection markdown content
            behavior_names: Behaviors to focus on (default: all)
            context: Optional context for evaluation

        Returns:
            Dictionary with evolved prompts and evolution metadata
        """
        context = context or {}
        behavior_names = behavior_names or list(evaluation_results.get("behaviors", {}).keys())

        # Get current prompt
        current_prompt = self.adapter.get_prompt()
        current_candidate = {"system_prompt": current_prompt}

        # Evaluate current candidate on minibatch
        current_score = evaluation_results.get("overall_score", 0.0)

        evolution_history = []
        best_candidate = current_candidate.copy()
        best_score = current_score

        for iteration in range(self.max_iterations):
            # Generate population of candidates
            candidates = self._generate_candidates(
                current_candidate=current_candidate,
                evaluation_results=evaluation_results,
                reflection=reflection,
                population_size=self.population_size,
            )

            # Evaluate candidates on minibatch
            candidate_scores = []
            for candidate in candidates:
                # Update adapter with candidate prompt
                self.adapter.update_prompt(candidate["system_prompt"])

                # Quick evaluation on minibatch
                minibatch_results = self._evaluate_minibatch(
                    behavior_names=behavior_names,
                    num_scenarios=self.minibatch_size,
                    context=context,
                )

                score = minibatch_results.get("overall_score", 0.0)
                candidate_scores.append((candidate, score))

            # Select best candidate
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            best_iteration_candidate, best_iteration_score = candidate_scores[0]

            # Check for improvement
            improvement = best_iteration_score - best_score

            evolution_history.append(
                {
                    "iteration": iteration + 1,
                    "candidates_tested": len(candidates),
                    "best_score": best_iteration_score,
                    "improvement": improvement,
                    "candidate": best_iteration_candidate,
                }
            )

            # Accept if improved
            if improvement >= self.improvement_threshold:
                best_candidate = best_iteration_candidate
                best_score = best_iteration_score
                current_candidate = best_iteration_candidate

                # Update adapter with best prompt
                self.adapter.update_prompt(best_candidate["system_prompt"])
            else:
                # No improvement, stop early
                break

        # Restore best prompt to adapter
        self.adapter.update_prompt(best_candidate["system_prompt"])

        # Prepare evolved prompts output
        evolved_prompts = {
            "agent": self.adapter.get_adapter_type(),
            "prompts": best_candidate,
            "metadata": {
                "iterations": len(evolution_history),
                "initial_score": current_score,
                "final_score": best_score,
                "improvement": best_score - current_score,
                "evolution_history": evolution_history,
            },
        }

        # Save evolved prompts
        if self.artifact_manager:
            run_id = evaluation_results.get("run_id")
            self.artifact_manager.save_evolved_prompts(evolved_prompts, run_id=run_id)

        return evolved_prompts

    def _generate_candidates(
        self,
        current_candidate: dict[str, str],
        evaluation_results: dict[str, Any],
        reflection: str,
        population_size: int,
    ) -> list[dict[str, str]]:
        """Generate population of candidate prompts."""
        candidates = []

        # Always include current candidate
        candidates.append(current_candidate.copy())

        # Generate new candidates
        for _ in range(population_size - 1):
            proposed_prompt = self.proposer.propose_improved_prompt(
                current_prompt=current_candidate["system_prompt"],
                evaluation_results=evaluation_results,
                reflection=reflection,
                component_name="system_prompt",
            )

            candidates.append({"system_prompt": proposed_prompt})

        return candidates

    def _evaluate_minibatch(
        self, behavior_names: list[str], num_scenarios: int, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Quick evaluation on a minibatch of scenarios."""
        # Use evaluation engine with reduced scenarios
        config = self.evaluation_engine.config.copy()
        config["scenario_generator"] = config.get("scenario_generator", {}).copy()
        config["scenario_generator"]["num_scenarios"] = num_scenarios

        # Create temporary evaluation engine with reduced config
        from codeoptix.evaluation import EvaluationEngine

        temp_engine = EvaluationEngine(self.adapter, self.llm_client, config=config)

        # Run evaluation
        results = temp_engine.evaluate_behaviors(behavior_names=behavior_names, context=context)

        return results
