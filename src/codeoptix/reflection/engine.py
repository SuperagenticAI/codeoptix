"""Reflection engine for CodeOptiX."""

from typing import Any

from codeoptix.artifacts.manager import ArtifactManager
from codeoptix.reflection.generator import ReflectionGenerator


class ReflectionEngine:
    """
    Reflection engine that analyzes evaluation results and generates insights.

    Generates human-readable reflection reports identifying root causes
    and providing actionable recommendations.
    """

    def __init__(
        self, artifact_manager: ArtifactManager | None = None, config: dict[str, Any] | None = None
    ):
        """
        Initialize reflection engine.

        Args:
            artifact_manager: Artifact manager for loading/saving
            config: Configuration dictionary
        """
        self.artifact_manager = artifact_manager or ArtifactManager()
        self.config = config or {}
        self.generator = ReflectionGenerator(self.config.get("generator", {}))

    def reflect(
        self, results: dict[str, Any], agent_name: str | None = None, save: bool = True
    ) -> str:
        """
        Generate reflection from evaluation results.

        Args:
            results: Evaluation results dictionary
            agent_name: Optional agent name
            save: Whether to save reflection to file

        Returns:
            Reflection markdown content
        """
        # Generate reflection content
        reflection_content = self.generator.generate(results, agent_name=agent_name)

        # Save if requested
        if save:
            run_id = results.get("run_id")
            self.artifact_manager.save_reflection(reflection_content, run_id=run_id)

        return reflection_content

    def reflect_from_run_id(self, run_id: str, agent_name: str | None = None) -> str:
        """
        Generate reflection from a previous evaluation run.

        Args:
            run_id: Run ID to load results from
            agent_name: Optional agent name

        Returns:
            Reflection markdown content
        """
        # Load results
        results = self.artifact_manager.load_results(run_id)

        # Generate reflection
        return self.reflect(results, agent_name=agent_name, save=True)
