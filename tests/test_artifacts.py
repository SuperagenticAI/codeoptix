"""Tests for artifact management."""

import json
from pathlib import Path

from codeoptix.artifacts import ArtifactManager


class TestArtifactManager:
    """Test artifact manager."""

    def test_artifact_manager_initialization(self, temp_artifacts_dir):
        """Test artifact manager initialization."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        assert manager.artifacts_dir == Path(temp_artifacts_dir)

    def test_save_results(self, temp_artifacts_dir, sample_evaluation_results):
        """Test saving evaluation results."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        results_path = manager.save_results(sample_evaluation_results)

        assert results_path.exists()
        assert results_path.suffix == ".json"

        # Verify content
        with open(results_path) as f:
            loaded = json.load(f)
        assert loaded["run_id"] == sample_evaluation_results["run_id"]

    def test_load_results(self, temp_artifacts_dir, sample_evaluation_results):
        """Test loading evaluation results."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        # Save results - this will generate a run_id if not provided
        saved_path = manager.save_results(
            sample_evaluation_results, run_id=sample_evaluation_results["run_id"]
        )

        loaded = manager.load_results(sample_evaluation_results["run_id"])
        assert loaded["run_id"] == sample_evaluation_results["run_id"]
        assert loaded["overall_score"] == sample_evaluation_results["overall_score"]

    def test_save_results_returns_path(self, temp_artifacts_dir, sample_evaluation_results):
        """Test that save_results returns correct path."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        path = manager.save_results(
            sample_evaluation_results, run_id=sample_evaluation_results["run_id"]
        )

        assert path.exists()
        assert sample_evaluation_results["run_id"] in str(path)
        assert path.suffix == ".json"

    def test_save_reflection(self, temp_artifacts_dir, sample_evaluation_results):
        """Test saving reflection."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        reflection_content = "# Reflection\n\nTest content"
        path = manager.save_reflection(
            reflection_content, run_id=sample_evaluation_results["run_id"]
        )

        assert path.exists()
        assert sample_evaluation_results["run_id"] in str(path)
        assert path.suffix == ".md"

        # Test loading
        loaded = manager.load_reflection(sample_evaluation_results["run_id"])
        assert "Test content" in loaded

    def test_save_evolved_prompts(self, temp_artifacts_dir, sample_evaluation_results):
        """Test saving evolved prompts."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        evolved = {"prompts": {"system_prompt": "New prompt"}}
        path = manager.save_evolved_prompts(evolved, run_id=sample_evaluation_results["run_id"])

        assert path.exists()
        assert sample_evaluation_results["run_id"] in str(path)
        assert path.suffix in [".yaml", ".yml"]

        # Test loading
        loaded = manager.load_evolved_prompts(sample_evaluation_results["run_id"])
        assert "prompts" in loaded

    def test_list_runs(self, temp_artifacts_dir, sample_evaluation_results):
        """Test listing evaluation runs."""
        manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)

        # Save multiple runs with explicit run_ids
        manager.save_results(sample_evaluation_results, run_id="test-run-001")

        # Create another run
        run2 = sample_evaluation_results.copy()
        run2["run_id"] = "test-run-002"
        manager.save_results(run2, run_id="test-run-002")

        runs = manager.list_runs()
        assert len(runs) >= 2
        run_ids = [r["run_id"] for r in runs]
        assert "test-run-001" in run_ids
        assert "test-run-002" in run_ids
