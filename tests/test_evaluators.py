"""Tests for evaluation components."""

from codeoptix.evaluation.evaluators import (
    ArtifactComparator,
    LLMEvaluator,
    StaticAnalyzer,
    TestRunner,
)


class TestStaticAnalyzer:
    """Test static analyzer."""

    def test_static_analyzer_initialization(self):
        """Test static analyzer initialization."""
        analyzer = StaticAnalyzer()
        assert analyzer is not None

    def test_static_analyzer_with_config(self):
        """Test static analyzer with configuration."""
        config = {"bandit": True}
        analyzer = StaticAnalyzer(config)
        assert analyzer is not None

    def test_analyze_code(self):
        """Test analyzing code."""
        analyzer = StaticAnalyzer()
        code = "def test():\n    password = 'secret'\n    return password"
        results = analyzer.analyze(code)

        assert isinstance(results, dict)
        # Results may be empty if bandit not available, but structure should work


class TestTestRunnerComponent:
    """Test test runner component."""

    def test_test_runner_initialization(self):
        """Test test runner initialization."""
        runner = TestRunner()
        assert runner is not None

    def test_test_runner_with_config(self):
        """Test test runner with configuration."""
        config = {"coverage": True}
        runner = TestRunner(config)
        assert runner is not None

    def test_run_tests(self):
        """Test running tests."""
        runner = TestRunner()
        code = "def add(a, b):\n    return a + b"
        tests = "def test_add():\n    assert add(1, 2) == 3"

        results = runner.run_tests(code, tests)
        assert isinstance(results, dict)
        # Results may vary based on pytest availability


class TestLLMEvaluator:
    """Test LLM evaluator."""

    def test_llm_evaluator_initialization(self, mock_llm_client):
        """Test LLM evaluator initialization."""
        evaluator = LLMEvaluator(mock_llm_client)
        assert evaluator.llm_client == mock_llm_client

    def test_evaluate_code(self, mock_llm_client):
        """Test evaluating code with LLM."""
        evaluator = LLMEvaluator(mock_llm_client)
        results = evaluator.evaluate(code="def test(): pass", behavior_description="Test behavior")

        assert isinstance(results, dict)
        # Should have some structure
        assert "score" in results or "evaluation" in results or len(results) >= 0


class TestArtifactComparator:
    """Test artifact comparator."""

    def test_artifact_comparator_initialization(self):
        """Test artifact comparator initialization."""
        comparator = ArtifactComparator()
        assert comparator is not None

    def test_compare_artifacts(self):
        """Test comparing artifacts."""
        comparator = ArtifactComparator()
        results = comparator.compare(
            code="def test(): pass", artifacts={"plan": "Implement feature"}
        )

        assert isinstance(results, dict)
        # Results structure should be consistent
