"""Tests for evaluation engine."""

from codeoptix.evaluation import EvaluationEngine
from codeoptix.evaluation.scenario_generator import BloomScenarioGenerator, ScenarioGenerator


class TestEvaluationEngine:
    """Test evaluation engine."""

    def test_evaluation_engine_initialization(self, mock_adapter, mock_llm_client):
        """Test evaluation engine initialization."""
        engine = EvaluationEngine(mock_adapter, mock_llm_client)
        assert engine.adapter == mock_adapter
        assert engine.llm_client == mock_llm_client
        assert engine.scenario_generator is not None

    def test_evaluation_engine_with_config(self, mock_adapter, mock_llm_client):
        """Test evaluation engine with configuration."""
        config = {
            "scenario_generator": {"num_scenarios": 2, "use_bloom": False},
            "static_analysis": {"bandit": True},
        }
        engine = EvaluationEngine(mock_adapter, mock_llm_client, config=config)
        assert isinstance(engine.scenario_generator, ScenarioGenerator)

    def test_evaluation_engine_with_bloom(self, mock_adapter, mock_llm_client):
        """Test evaluation engine with Bloom scenario generator."""
        config = {"scenario_generator": {"use_bloom": True, "num_scenarios": 2}}
        engine = EvaluationEngine(mock_adapter, mock_llm_client, config=config)
        assert isinstance(engine.scenario_generator, BloomScenarioGenerator)

    def test_evaluate_behaviors(self, mock_adapter, mock_llm_client):
        """Test evaluating behaviors."""
        engine = EvaluationEngine(
            mock_adapter,
            mock_llm_client,
            config={"scenario_generator": {"num_scenarios": 1, "use_bloom": False}},
        )

        results = engine.evaluate_behaviors(
            behavior_names=["insecure-code"],
            scenarios=[
                {"prompt": "Write a function", "task": "Test task", "behavior": "insecure-code"}
            ],
        )

        assert "behaviors" in results
        assert "overall_score" in results
        assert "insecure-code" in results["behaviors"]
        assert 0.0 <= results["overall_score"] <= 1.0

    def test_evaluate_multiple_behaviors(self, mock_adapter, mock_llm_client):
        """Test evaluating multiple behaviors."""
        engine = EvaluationEngine(
            mock_adapter,
            mock_llm_client,
            config={"scenario_generator": {"num_scenarios": 1, "use_bloom": False}},
        )

        results = engine.evaluate_behaviors(behavior_names=["insecure-code", "vacuous-tests"])

        assert len(results["behaviors"]) == 2
        assert "insecure-code" in results["behaviors"]
        assert "vacuous-tests" in results["behaviors"]

    def test_evaluate_with_context(self, mock_adapter, mock_llm_client):
        """Test evaluation with context."""
        engine = EvaluationEngine(
            mock_adapter,
            mock_llm_client,
            config={"scenario_generator": {"num_scenarios": 1, "use_bloom": False}},
        )

        context = {
            "plan": "Implement secure authentication",
            "requirements": ["No hardcoded secrets", "Include tests"],
        }

        results = engine.evaluate_behaviors(behavior_names=["insecure-code"], context=context)

        assert results is not None
        assert "behaviors" in results


class TestScenarioGenerator:
    """Test scenario generator."""

    def test_scenario_generator_initialization(self, mock_llm_client):
        """Test scenario generator initialization."""
        generator = ScenarioGenerator(mock_llm_client)
        assert generator.llm_client == mock_llm_client
        assert generator.num_scenarios == 3  # Default

    def test_generate_scenarios(self, mock_llm_client):
        """Test generating scenarios."""
        generator = ScenarioGenerator(mock_llm_client, config={"num_scenarios": 2})
        scenarios = generator.generate_scenarios(
            behavior_name="insecure-code", behavior_description="Detect insecure code"
        )

        assert isinstance(scenarios, list)
        assert len(scenarios) <= 2

    def test_bloom_scenario_generator(self, mock_llm_client):
        """Test Bloom scenario generator."""
        generator = BloomScenarioGenerator(mock_llm_client, config={"num_scenarios": 2})
        scenarios = generator.generate_scenarios(
            behavior_name="insecure-code",
            behavior_description="Detect insecure code",
            examples=[{"task": "Test", "prompt": "Write code"}],
        )

        assert isinstance(scenarios, list)
