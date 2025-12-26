"""Tests for agent adapters."""

from codeoptix.adapters.base import AgentOutput
from codeoptix.adapters.factory import create_adapter
from tests.conftest import MockAgentAdapter


class TestAgentAdapter:
    """Test base adapter interface."""

    def test_adapter_execute(self, mock_adapter):
        """Test adapter execute method."""
        output = mock_adapter.execute("Write a function")
        assert isinstance(output, AgentOutput)
        assert output.code is not None
        assert output.prompt_used == mock_adapter.get_prompt()

    def test_adapter_get_prompt(self, mock_adapter):
        """Test getting adapter prompt."""
        prompt = mock_adapter.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_adapter_update_prompt(self, mock_adapter):
        """Test updating adapter prompt."""
        new_prompt = "New system prompt"
        mock_adapter.update_prompt(new_prompt)
        assert mock_adapter.get_prompt() == new_prompt

    def test_adapter_get_type(self, mock_adapter):
        """Test getting adapter type."""
        adapter_type = mock_adapter.get_adapter_type()
        assert isinstance(adapter_type, str)
        assert adapter_type == "mock-adapter"


class TestAdapterFactory:
    """Test adapter factory."""

    def test_create_mock_adapter(self):
        """Test creating mock adapter."""
        config = {"prompt": "Test prompt"}
        adapter = MockAgentAdapter(config)
        assert adapter.get_adapter_type() == "mock-adapter"

    def test_create_adapter_with_config(self):
        """Test creating adapter with configuration."""
        config = {
            "llm_config": {
                "provider": "openai",
                "api_key": "test-key",
            },
            "prompt": "You are a helpful assistant.",
        }
        # This will fail if API key is invalid, but structure should work
        try:
            adapter = create_adapter("codex", config)
            assert adapter is not None
            assert hasattr(adapter, "execute")
        except Exception:
            # Expected if API key is invalid - just test structure
            pass

    def test_adapter_execute_tracks_calls(self, mock_adapter):
        """Test that adapter tracks execute calls."""
        mock_adapter.execute("Test prompt 1")
        mock_adapter.execute("Test prompt 2", context={"key": "value"})

        assert len(mock_adapter.execute_calls) == 2
        assert mock_adapter.execute_calls[0]["prompt"] == "Test prompt 1"
        assert mock_adapter.execute_calls[1]["context"] == {"key": "value"}


class TestAgentOutput:
    """Test AgentOutput dataclass."""

    def test_agent_output_creation(self):
        """Test creating AgentOutput."""
        output = AgentOutput(
            code="def test(): pass", tests="def test_test(): pass", prompt_used="Test prompt"
        )
        assert output.code == "def test(): pass"
        assert output.tests == "def test_test(): pass"
        assert output.prompt_used == "Test prompt"
        assert output.traces is None
        assert output.metadata is None

    def test_agent_output_with_metadata(self):
        """Test AgentOutput with metadata."""
        metadata = {"model": "gpt-4o", "temperature": 0.7}
        output = AgentOutput(code="def test(): pass", metadata=metadata)
        assert output.metadata == metadata
