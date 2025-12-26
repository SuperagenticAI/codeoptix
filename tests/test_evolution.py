"""Tests for evolution engine."""

from codeoptix.artifacts import ArtifactManager
from codeoptix.evaluation import EvaluationEngine
from codeoptix.evolution import EvolutionEngine


class TestEvolutionEngine:
    """Test evolution engine."""

    def test_evolution_engine_initialization(
        self, mock_adapter, mock_llm_client, temp_artifacts_dir
    ):
        """Test evolution engine initialization."""
        eval_engine = EvaluationEngine(mock_adapter, mock_llm_client)
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)

        evolution_engine = EvolutionEngine(
            adapter=mock_adapter,
            evaluation_engine=eval_engine,
            llm_client=mock_llm_client,
            artifact_manager=artifact_manager,
        )

        assert evolution_engine.adapter == mock_adapter
        assert evolution_engine.evaluation_engine == eval_engine
        assert evolution_engine.llm_client == mock_llm_client

    def test_evolution_engine_with_config(self, mock_adapter, mock_llm_client, temp_artifacts_dir):
        """Test evolution engine with configuration."""
        eval_engine = EvaluationEngine(mock_adapter, mock_llm_client)
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)

        config = {"max_iterations": 2, "population_size": 2, "minibatch_size": 1}

        evolution_engine = EvolutionEngine(
            adapter=mock_adapter,
            evaluation_engine=eval_engine,
            llm_client=mock_llm_client,
            artifact_manager=artifact_manager,
            config=config,
        )

        assert evolution_engine.max_iterations == 2
        assert evolution_engine.population_size == 2

    def test_evolve_returns_results(
        self,
        mock_adapter,
        mock_llm_client,
        temp_artifacts_dir,
        sample_evaluation_results,
        sample_reflection_content,
    ):
        """Test that evolve returns results."""
        eval_engine = EvaluationEngine(
            mock_adapter,
            mock_llm_client,
            config={"scenario_generator": {"num_scenarios": 1, "use_bloom": False}},
        )
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)

        config = {"max_iterations": 1, "population_size": 1, "minibatch_size": 1}

        evolution_engine = EvolutionEngine(
            adapter=mock_adapter,
            evaluation_engine=eval_engine,
            llm_client=mock_llm_client,
            artifact_manager=artifact_manager,
            config=config,
        )

        evolved = evolution_engine.evolve(
            evaluation_results=sample_evaluation_results,
            reflection=sample_reflection_content,
            behavior_names=["insecure-code"],
        )

        assert "prompts" in evolved
        assert "metadata" in evolved
        assert "system_prompt" in evolved["prompts"]
        assert "iterations" in evolved["metadata"]

    def test_evolve_saves_artifacts(
        self,
        mock_adapter,
        mock_llm_client,
        temp_artifacts_dir,
        sample_evaluation_results,
        sample_reflection_content,
    ):
        """Test that evolve saves artifacts."""
        eval_engine = EvaluationEngine(
            mock_adapter,
            mock_llm_client,
            config={"scenario_generator": {"num_scenarios": 1, "use_bloom": False}},
        )
        artifact_manager = ArtifactManager(artifacts_dir=temp_artifacts_dir)

        config = {"max_iterations": 1, "population_size": 1, "minibatch_size": 1}

        evolution_engine = EvolutionEngine(
            adapter=mock_adapter,
            evaluation_engine=eval_engine,
            llm_client=mock_llm_client,
            artifact_manager=artifact_manager,
            config=config,
        )

        evolved = evolution_engine.evolve(
            evaluation_results=sample_evaluation_results,
            reflection=sample_reflection_content,
            behavior_names=["insecure-code"],
        )

        # Check that evolved prompts file exists
        evolved_path = (
            temp_artifacts_dir / f"evolved_prompts_{sample_evaluation_results['run_id']}.yaml"
        )
        assert evolved_path.exists()
        assert "prompts" in evolved
