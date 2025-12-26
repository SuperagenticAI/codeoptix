"""Test error handling in adapters."""

import pytest

from codeoptix.adapters.factory import create_adapter


class TestAdapterErrorHandling:
    """Test error handling in adapters."""

    def test_create_adapter_invalid_type(self):
        """Test creating adapter with invalid type."""
        with pytest.raises(ValueError, match="Unsupported adapter type"):
            create_adapter("invalid-type", {})

    def test_create_adapter_invalid_provider(self):
        """Test creating adapter with invalid provider."""
        config = {"llm_config": {"provider": "invalid"}}
        with pytest.raises(ValueError):
            create_adapter("claude-code", config)
