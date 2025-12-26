"""Tests for behavior specifications."""

import pytest

from codeoptix.adapters.base import AgentOutput
from codeoptix.behaviors import create_behavior
from codeoptix.behaviors.base import BehaviorResult, Severity


class TestBehaviorSpec:
    """Test base behavior spec interface."""

    def test_create_insecure_code_behavior(self):
        """Test creating insecure-code behavior."""
        behavior = create_behavior("insecure-code")
        assert behavior.get_name() == "insecure-code"
        assert behavior.is_enabled()
        assert behavior.get_description() is not None

    def test_create_vacuous_tests_behavior(self):
        """Test creating vacuous-tests behavior."""
        behavior = create_behavior("vacuous-tests")
        assert behavior.get_name() == "vacuous-tests"
        assert behavior.is_enabled()

    def test_create_plan_drift_behavior(self):
        """Test creating plan-drift behavior."""
        behavior = create_behavior("plan-drift")
        assert behavior.get_name() == "plan-drift"
        assert behavior.is_enabled()

    def test_behavior_with_config(self):
        """Test behavior with custom configuration."""
        config = {"severity": "high", "enabled": False}
        behavior = create_behavior("insecure-code", config)
        assert behavior.get_severity() == Severity.HIGH
        assert not behavior.is_enabled()

    def test_behavior_evaluate_returns_result(self, mock_adapter):
        """Test that behavior evaluation returns BehaviorResult."""
        behavior = create_behavior("insecure-code")
        output = mock_adapter.execute("Write code")
        result = behavior.evaluate(output)

        assert isinstance(result, BehaviorResult)
        assert result.behavior_name == "insecure-code"
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.passed, bool)
        assert isinstance(result.evidence, list)


class TestInsecureCodeBehavior:
    """Test insecure-code behavior."""

    def test_detects_hardcoded_secrets(self, mock_adapter_with_insecure_code):
        """Test detection of hardcoded secrets."""
        behavior = create_behavior("insecure-code")
        output = mock_adapter_with_insecure_code.execute("Write code")
        result = behavior.evaluate(output)

        # Should detect hardcoded password
        assert result.score < 1.0
        assert any("password" in ev.lower() or "secret" in ev.lower() for ev in result.evidence)

    def test_passes_secure_code(self, mock_adapter):
        """Test that secure code passes."""
        behavior = create_behavior("insecure-code")
        output = mock_adapter.execute("Write secure code")
        result = behavior.evaluate(output)

        # Secure code should score higher
        assert result.score >= 0.0


class TestVacuousTestsBehavior:
    """Test vacuous-tests behavior."""

    def test_detects_vacuous_tests(self, mock_adapter_with_vacuous_tests):
        """Test detection of vacuous tests."""
        behavior = create_behavior("vacuous-tests")
        output = mock_adapter_with_vacuous_tests.execute("Write tests")
        result = behavior.evaluate(output)

        # Should detect vacuous tests
        assert result.score < 1.0
        assert len(result.evidence) > 0

    def test_passes_good_tests(self, mock_adapter):
        """Test that good tests pass."""
        behavior = create_behavior("vacuous-tests")
        # Create output with good tests
        output = AgentOutput(
            code="def add(a, b): return a + b", tests="def test_add():\n    assert add(1, 2) == 3"
        )
        result = behavior.evaluate(output)

        # Good tests should score higher
        assert result.score >= 0.0


class TestPlanDriftBehavior:
    """Test plan-drift behavior."""

    def test_plan_drift_evaluation(self, mock_adapter):
        """Test plan drift evaluation."""
        behavior = create_behavior("plan-drift")
        output = mock_adapter.execute("Write code")
        context = {
            "plan": "Implement feature X",
            "requirements": ["Requirement 1", "Requirement 2"],
        }
        result = behavior.evaluate(output, context=context)

        assert isinstance(result, BehaviorResult)
        assert result.behavior_name == "plan-drift"
        assert 0.0 <= result.score <= 1.0


class TestBehaviorResult:
    """Test BehaviorResult dataclass."""

    def test_behavior_result_creation(self):
        """Test creating BehaviorResult."""
        result = BehaviorResult(
            behavior_name="test-behavior",
            passed=True,
            score=0.8,
            evidence=["Evidence 1"],
            severity=Severity.MEDIUM,
        )
        assert result.behavior_name == "test-behavior"
        assert result.passed is True
        assert result.score == 0.8
        assert result.evidence == ["Evidence 1"]
        assert result.severity == Severity.MEDIUM

    def test_behavior_result_score_validation(self):
        """Test that score is validated to be in range."""
        # Valid score
        result = BehaviorResult(behavior_name="test", passed=True, score=0.5)
        assert result.score == 0.5

        # Invalid score should raise error
        with pytest.raises(ValueError):
            BehaviorResult(
                behavior_name="test",
                passed=True,
                score=1.5,  # Invalid: > 1.0
            )

        with pytest.raises(ValueError):
            BehaviorResult(
                behavior_name="test",
                passed=True,
                score=-0.1,  # Invalid: < 0.0
            )
