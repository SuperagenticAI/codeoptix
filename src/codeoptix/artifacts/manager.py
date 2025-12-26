"""Artifact management for CodeOptix."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml


class ArtifactManager:
    """Manages storage and retrieval of CodeOptix artifacts."""

    def __init__(self, artifacts_dir: str | Path | None = None):
        """
        Initialize artifact manager.

        Args:
            artifacts_dir: Directory for storing artifacts (default: .codeoptix/artifacts)
        """
        if artifacts_dir is None:
            artifacts_dir = Path(".codeoptix") / "artifacts"

        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def save_results(self, results: dict[str, Any], run_id: str | None = None) -> Path:
        """
        Save evaluation results to JSON file.

        Args:
            results: Evaluation results dictionary
            run_id: Optional run ID (generated if not provided)

        Returns:
            Path to saved results file
        """
        if run_id is None:
            run_id = self._generate_run_id()

        # Add metadata
        results_with_metadata = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            **results,
        }

        # Save to file
        results_file = self.artifacts_dir / f"results_{run_id}.json"
        with open(results_file, "w") as f:
            json.dump(results_with_metadata, f, indent=2, default=str)

        return results_file

    def load_results(self, run_id: str) -> dict[str, Any]:
        """
        Load evaluation results by run ID.

        Args:
            run_id: Run ID to load

        Returns:
            Results dictionary
        """
        results_file = self.artifacts_dir / f"results_{run_id}.json"

        if not results_file.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")

        with open(results_file) as f:
            return json.load(f)

    def save_reflection(self, reflection_content: str, run_id: str | None = None) -> Path:
        """
        Save reflection markdown file.

        Args:
            reflection_content: Reflection markdown content
            run_id: Optional run ID (generated if not provided)

        Returns:
            Path to saved reflection file
        """
        if run_id is None:
            run_id = self._generate_run_id()

        reflection_file = self.artifacts_dir / f"reflection_{run_id}.md"
        with open(reflection_file, "w") as f:
            f.write(reflection_content)

        return reflection_file

    def load_reflection(self, run_id: str) -> str:
        """
        Load reflection markdown by run ID.

        Args:
            run_id: Run ID to load

        Returns:
            Reflection markdown content
        """
        reflection_file = self.artifacts_dir / f"reflection_{run_id}.md"

        if not reflection_file.exists():
            raise FileNotFoundError(f"Reflection file not found: {reflection_file}")

        with open(reflection_file) as f:
            return f.read()

    def save_evolved_prompts(
        self, evolved_prompts: dict[str, Any], run_id: str | None = None
    ) -> Path:
        """
        Save evolved prompts to YAML file.

        Args:
            evolved_prompts: Evolved prompts dictionary
            run_id: Optional run ID (generated if not provided)

        Returns:
            Path to saved prompts file
        """
        if run_id is None:
            run_id = self._generate_run_id()

        # Add metadata
        prompts_with_metadata = {
            "version": "0.1.0",
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            **evolved_prompts,
        }

        prompts_file = self.artifacts_dir / f"evolved_prompts_{run_id}.yaml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_with_metadata, f, default_flow_style=False, sort_keys=False)

        return prompts_file

    def load_evolved_prompts(self, run_id: str) -> dict[str, Any]:
        """
        Load evolved prompts by run ID.

        Args:
            run_id: Run ID to load

        Returns:
            Evolved prompts dictionary
        """
        prompts_file = self.artifacts_dir / f"evolved_prompts_{run_id}.yaml"

        if not prompts_file.exists():
            raise FileNotFoundError(f"Evolved prompts file not found: {prompts_file}")

        with open(prompts_file) as f:
            return yaml.safe_load(f)

    def list_runs(self) -> list[dict[str, Any]]:
        """
        List all evaluation runs.

        Returns:
            List of run metadata dictionaries
        """
        runs = []

        # Find all results files
        for results_file in self.artifacts_dir.glob("results_*.json"):
            try:
                run_id = results_file.stem.replace("results_", "")
                with open(results_file) as f:
                    data = json.load(f)
                    runs.append(
                        {
                            "run_id": run_id,
                            "timestamp": data.get("timestamp"),
                            "overall_score": data.get("overall_score"),
                            "behaviors": list(data.get("behaviors", {}).keys()),
                        }
                    )
            except Exception:
                continue

        # Sort by timestamp (newest first)
        runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return runs

    def _generate_run_id(self) -> str:
        """Generate a unique run ID."""
        return str(uuid4())[:8]
