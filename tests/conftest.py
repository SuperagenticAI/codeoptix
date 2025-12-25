"""Pytest configuration and shared fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.utils.llm import LLMClient


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self, responses: Dict[str, str] = None):
        """Initialize mock LLM client with predefined responses."""
        self.responses = responses or {}
        self.call_history = []
        self.config = {"model": "gpt-4o"}
    
    def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Return mock response based on prompt content."""
        prompt = messages[-1]["content"] if messages else ""
        self.call_history.append({
            "messages": messages,
            "model": model,
            "temperature": temperature,
            **kwargs
        })
        
        # Return predefined response or default
        for key, response in self.responses.items():
            if key.lower() in prompt.lower():
                return response
        
        # Default responses based on prompt type
        if "scenario" in prompt.lower() or "generate" in prompt.lower():
            return json.dumps([
                {
                    "task": "Test task",
                    "prompt": "Write a test function",
                    "expected_issues": ["test issue"]
                }
            ])
        elif "evaluate" in prompt.lower() or "judge" in prompt.lower():
            return "The code looks good. Score: 0.8/1.0"
        elif "reflect" in prompt.lower() or "analysis" in prompt.lower():
            return "## Reflection\n\nThe code has some issues that need addressing."
        elif "improve" in prompt.lower() or "propose" in prompt.lower():
            return "Improved prompt: Write secure code without hardcoded secrets."
        else:
            return "Mock LLM response"


class MockAgentAdapter(AgentAdapter):
    """Mock agent adapter for testing."""
    
    def __init__(self, config: Dict[str, Any] = None, output: AgentOutput = None):
        """Initialize mock adapter with config and optional output."""
        super().__init__(config or {})
        self._output = output or AgentOutput(
            code="def test_function():\n    return 'test'",
            tests="def test_test_function():\n    assert test_function() == 'test'",
            prompt_used="You are a helpful assistant."
        )
        self._prompt = config.get("prompt", "You are a helpful assistant.") if config else "You are a helpful assistant."
        self.execute_calls = []
    
    def execute(self, prompt: str, context: Dict[str, Any] = None) -> AgentOutput:
        """Return mock output."""
        self.execute_calls.append({"prompt": prompt, "context": context})
        # Modify output based on prompt if needed
        output = AgentOutput(
            code=self._output.code,
            tests=self._output.tests,
            prompt_used=self._prompt,
            metadata={"mock": True}
        )
        return output
    
    def get_prompt(self) -> str:
        """Return current prompt."""
        return self._prompt
    
    def update_prompt(self, new_prompt: str) -> None:
        """Update prompt."""
        self._prompt = new_prompt
    
    def get_adapter_type(self) -> str:
        """Return adapter type."""
        return "mock-adapter"


@pytest.fixture
def mock_llm_client():
    """Fixture for mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def mock_adapter():
    """Fixture for mock agent adapter."""
    return MockAgentAdapter()


@pytest.fixture
def mock_adapter_with_insecure_code():
    """Fixture for mock adapter that produces insecure code."""
    return MockAgentAdapter(
        output=AgentOutput(
            code='def connect_db():\n    password = "hardcoded_secret_123"\n    return password',
            tests="def test_connect_db():\n    assert True",
            prompt_used="Write database connection code"
        )
    )


@pytest.fixture
def mock_adapter_with_vacuous_tests():
    """Fixture for mock adapter that produces vacuous tests."""
    return MockAgentAdapter(
        output=AgentOutput(
            code="def add(a, b):\n    return a + b",
            tests="def test_add():\n    pass  # No assertions",
            prompt_used="Write a function and tests"
        )
    )


@pytest.fixture
def temp_artifacts_dir():
    """Fixture for temporary artifacts directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_evaluation_results():
    """Fixture for sample evaluation results."""
    return {
        "run_id": "test-run-001",
        "timestamp": "2025-01-20T10:00:00Z",
        "agent": "mock-adapter",
        "overall_score": 0.65,
        "behaviors": {
            "insecure-code": {
                "behavior_name": "insecure-code",
                "scenarios_tested": 2,
                "scenarios_passed": 1,
                "score": 0.5,
                "passed": False,
                "evidence": ["Hardcoded password found", "SQL injection risk"],
                "scenario_results": [
                    {
                        "scenario": {"prompt": "Write secure code"},
                        "behavior_result": {
                            "passed": False,
                            "score": 0.5,
                            "evidence": ["Hardcoded password"]
                        }
                    }
                ]
            },
            "vacuous-tests": {
                "behavior_name": "vacuous-tests",
                "scenarios_tested": 1,
                "scenarios_passed": 0,
                "score": 0.3,
                "passed": False,
                "evidence": ["No assertions in tests"],
                "scenario_results": []
            }
        },
        "metadata": {}
    }


@pytest.fixture
def sample_reflection_content():
    """Fixture for sample reflection markdown content."""
    return """# Reflection Report

## Summary
The evaluation identified several issues with the agent's behavior.

## Root Causes
1. Hardcoded secrets in code
2. Missing test assertions

## Recommendations
1. Add explicit instructions to avoid hardcoded secrets
2. Require assertions in all tests
"""

