"""Tests for reflection engine."""

from codeoptix.artifacts import ArtifactManager
from codeoptix.reflection import ReflectionEngine


class TestReflectionEngine:
    """Test reflection engine."""

    def test_reflection_engine_initialization(self, temp_artifacts_dir):
        """Test reflection engine initialization."""
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        engine = ReflectionEngine(artifact_manager)
        assert engine.artifact_manager == artifact_manager

    def test_reflect_generates_content(self, temp_artifacts_dir, sample_evaluation_results):
        """Test that reflection generates content."""
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        engine = ReflectionEngine(artifact_manager)

        reflection = engine.reflect(results=sample_evaluation_results, agent_name="test-agent")

        assert isinstance(reflection, str)
        assert len(reflection) > 0
        # Should contain key sections
        assert "reflection" in reflection.lower() or "summary" in reflection.lower()

    def test_reflect_saves_to_file(self, temp_artifacts_dir, sample_evaluation_results):
        """Test that reflection saves to file."""
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        engine = ReflectionEngine(artifact_manager)

        # Save results first
        artifact_manager.save_results(
            sample_evaluation_results, run_id=sample_evaluation_results["run_id"]
        )

        reflection = engine.reflect(
            results=sample_evaluation_results, agent_name="test-agent", save=True
        )

        # Check that reflection file exists by loading it
        reflection_content = artifact_manager.load_reflection(sample_evaluation_results["run_id"])
        assert len(reflection_content) > 0

    def test_reflect_from_run_id(self, temp_artifacts_dir, sample_evaluation_results):
        """Test reflecting from run ID."""
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        engine = ReflectionEngine(artifact_manager)

        # Save results
        run_id = sample_evaluation_results["run_id"]
        artifact_manager.save_results(sample_evaluation_results, run_id=run_id)

        reflection = engine.reflect_from_run_id(run_id)

        assert isinstance(reflection, str)
        assert len(reflection) > 0

    def test_reflect_analyzes_failures(self, temp_artifacts_dir, sample_evaluation_results):
        """Test that reflection analyzes failures."""
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)
        engine = ReflectionEngine(artifact_manager)

        reflection = engine.reflect(results=sample_evaluation_results, agent_name="test-agent")

        # Should mention failed behaviors
        assert "insecure-code" in reflection.lower() or "vacuous-tests" in reflection.lower()
