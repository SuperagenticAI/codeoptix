"""Test behaviors for coverage."""

from codeoptix.adapters import AgentOutput
from codeoptix.behaviors import create_behavior


class TestBehaviorsCoverage:
    """Test behaviors to improve coverage."""

    def test_insecure_code_behavior_with_secure_code(self):
        """Test insecure code behavior with secure code."""
        behavior = create_behavior("insecure-code")
        agent_output = AgentOutput(
            code="def hello():\n    return 'world'",
            tests="def test_hello():\n    assert hello() == 'world'",
            prompt_used="Write hello function",
        )

        result = behavior.evaluate(agent_output)
        assert result.passed is True or result.score > 0.5  # Should pass or have good score

    def test_insecure_code_behavior_with_hardcoded_secret(self):
        """Test insecure code behavior detects hardcoded secrets."""
        behavior = create_behavior("insecure-code")
        agent_output = AgentOutput(
            code="def connect_db():\n    password = 'secret123'\n    return password",
            tests="def test_connect():\n    assert True",
            prompt_used="Write database connection",
        )

        result = behavior.evaluate(agent_output)
        assert result.passed is False  # Should fail
        assert "secret" in str(result.evidence).lower()

    def test_vacuous_tests_behavior_good_tests(self):
        """Test vacuous tests behavior with good tests."""
        behavior = create_behavior("vacuous-tests")
        agent_output = AgentOutput(
            code="def add(a, b):\n    return a + b",
            tests="def test_add():\n    assert add(1, 2) == 3\n    assert add(0, 0) == 0",
            prompt_used="Write add function",
        )

        result = behavior.evaluate(agent_output)
        assert result.passed is True  # Should pass with proper assertions

    def test_vacuous_tests_behavior_no_assertions(self):
        """Test vacuous tests behavior detects missing assertions."""
        behavior = create_behavior("vacuous-tests")
        agent_output = AgentOutput(
            code="def subtract(a, b):\n    return a - b",
            tests="def test_subtract():\n    result = subtract(5, 3)\n    # No assertion",
            prompt_used="Write subtract function",
        )

        result = behavior.evaluate(agent_output)
        assert result.passed is False  # Should fail without assertions

    def test_plan_drift_behavior_accurate_plan(self):
        """Test plan drift behavior with accurate implementation."""
        behavior = create_behavior("plan-drift")
        agent_output = AgentOutput(
            code="def calculate_total(items):\n    return sum(items)",
            tests="def test_total():\n    assert calculate_total([1, 2, 3]) == 6",
            prompt_used="Write function to calculate total of items",
        )

        result = behavior.evaluate(
            agent_output, context={"plan": "Write function to calculate total of items"}
        )
        assert result.behavior_name == "plan-drift"
        assert isinstance(result.score, float)  # Just check it runs and returns proper result
