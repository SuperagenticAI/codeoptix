"""Basic example of using CodeFlect adapters."""

import os
from codeoptix.adapters.factory import create_adapter


def example_claude_code():
    """Example using Claude Code adapter."""
    print("=== Claude Code Adapter Example ===\n")
    
    config = {
        "llm_config": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
        },
        "prompt": "You are a helpful coding assistant.",
    }
    
    adapter = create_adapter("claude-code", config)
    
    # Execute a simple task
    result = adapter.execute("Write a Python function to calculate fibonacci numbers")
    
    print(f"Code generated:\n{result.code}\n")
    print(f"Tests: {result.tests}\n")
    print(f"Metadata: {result.metadata}\n")


def example_codex():
    """Example using Codex adapter."""
    print("=== Codex Adapter Example ===\n")
    
    config = {
        "llm_config": {
            "provider": "openai",
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "prompt": "You are an expert Python programmer.",
    }
    
    adapter = create_adapter("codex", config)
    
    # Execute a simple task
    result = adapter.execute("Write a Python function to reverse a string")
    
    print(f"Code generated:\n{result.code}\n")
    print(f"Metadata: {result.metadata}\n")


def example_gemini_cli():
    """Example using Gemini CLI adapter."""
    print("=== Gemini CLI Adapter Example ===\n")
    
    config = {
        "llm_config": {
            "provider": "google",
            "model": "gemini-1.5-pro",
            "api_key": os.getenv("GOOGLE_API_KEY"),
        },
        "prompt": "You are a helpful coding assistant.",
        "use_cli": False,  # Use SDK instead of CLI
    }
    
    adapter = create_adapter("gemini-cli", config)
    
    # Execute a simple task
    result = adapter.execute("Write a Python function to check if a number is prime")
    
    print(f"Code generated:\n{result.code}\n")
    print(f"Metadata: {result.metadata}\n")


if __name__ == "__main__":
    # Uncomment the example you want to run (requires API keys)
    # example_claude_code()
    # example_codex()
    # example_gemini_cli()
    
    print("Examples are ready. Uncomment the function you want to test.")
    print("Make sure to set the appropriate API key environment variable:")
    print("  - ANTHROPIC_API_KEY for Claude Code")
    print("  - OPENAI_API_KEY for Codex")
    print("  - GOOGLE_API_KEY for Gemini CLI")

