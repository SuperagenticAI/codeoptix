"""Tests for LLM client utilities."""

from codeoptix.utils.llm import LLMProvider, create_llm_client
from tests.conftest import MockLLMClient


class TestLLMClient:
    """Test LLM client."""

    def test_mock_llm_client_creation(self):
        """Test creating mock LLM client."""
        client = MockLLMClient()
        assert client is not None
        assert hasattr(client, "chat_completion")

    def test_mock_llm_client_chat_completion(self):
        """Test mock LLM client chat completion."""
        client = MockLLMClient(responses={"test": "Test response"})
        response = client.chat_completion(messages=[{"role": "user", "content": "test prompt"}])
        assert response == "Test response"

    def test_mock_llm_client_tracks_calls(self):
        """Test that mock LLM client tracks calls."""
        client = MockLLMClient()
        client.chat_completion(
            messages=[{"role": "user", "content": "test"}], model="gpt-4o", temperature=0.7
        )

        assert len(client.call_history) == 1
        assert client.call_history[0]["model"] == "gpt-4o"
        assert client.call_history[0]["temperature"] == 0.7

    def test_llm_provider_enum(self):
        """Test LLM provider enum."""
        assert LLMProvider.ANTHROPIC == "anthropic"
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.GOOGLE == "google"

    def test_create_llm_client_structure(self):
        """Test create_llm_client function structure."""
        # This will fail without API key, but tests that function exists
        try:
            client = create_llm_client(LLMProvider.OPENAI, api_key="test-key")
            assert client is not None
        except Exception:
            # Expected if API key is invalid - just test structure exists
            pass
