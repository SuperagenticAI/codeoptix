"""Claude Code adapter for CodeOptix.

This adapter interfaces with Claude Code by using the Anthropic API directly,
which is what Claude Code uses under the hood. Since Claude Code is not open source,
we use the Anthropic SDK to match the same API patterns.

Note: Claude Code is a full CLI tool with plugins, hooks, and agents. This adapter
provides a simplified interface for CodeOptix's evaluation framework using the
same Anthropic API that Claude Code uses.
"""

import os
from typing import Any

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.utils.llm import LLMProvider, create_llm_client


class ClaudeCodeAdapter(AgentAdapter):
    """
    Adapter for Claude Code (Anthropic's coding agent).

    Claude Code uses the Anthropic Messages API. This adapter uses the same
    API directly to match Claude Code's behavior. The adapter follows the
    patterns from the Anthropic Python SDK reference implementation.

    Since Claude Code is not open source, we use the Anthropic API directly,
    which is the same API that Claude Code uses internally.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize Claude Code adapter."""
        super().__init__(config)

        # Get LLM configuration
        llm_config = config.get("llm_config", {})
        # Respect provider from config (defaults to ANTHROPIC for backward compatibility)
        provider_name = llm_config.get("provider", "anthropic").upper()
        try:
            provider = LLMProvider[provider_name]
        except KeyError as e:
            supported_providers = ", ".join([p.value for p in LLMProvider])
            raise ValueError(
                f"Invalid LLM provider '{provider_name}'. "
                f"Supported providers: {supported_providers}"
            ) from e

        # Get API key (not required for Ollama)
        api_key = None
        if provider != LLMProvider.OLLAMA:
            api_key = (
                llm_config.get("api_key")
                or os.getenv(f"{provider_name}_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
            )

        self.llm_client = create_llm_client(provider, api_key=api_key)
        # Use model from config, or default based on provider
        if provider == LLMProvider.OLLAMA:
            self.model = llm_config.get("model", "llama3.1:8b")
        else:
            # Use current Claude Code default model (claude-opus-4-5-20251101)
            self.model = llm_config.get("model", "claude-opus-4-5-20251101")
        self.temperature = llm_config.get("temperature", 1.0)
        self.max_tokens = llm_config.get("max_tokens", 4096)

        # Get initial prompt if provided
        self._current_prompt = config.get("prompt") or self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Get default Claude Code system prompt.

        This matches the style of prompts used in Claude Code plugins and
        follows Claude Code's best practices for coding assistants.
        """
        return """You are a helpful coding assistant. You write clean, secure, and well-tested code.
Follow best practices:
- Write secure code (no hardcoded secrets, validate inputs)
- Write meaningful tests
- Follow the user's requirements and planning artifacts
- Use appropriate error handling
- Write clear, maintainable code"""

    def execute(self, prompt: str, context: dict[str, Any] | None = None) -> AgentOutput:
        """
        Execute Claude Code with a task prompt.

        Uses the Anthropic Messages API (same API that Claude Code uses) to
        generate code and test responses. Follows the patterns from the
        Anthropic Python SDK reference implementation.
        """
        context = context or {}

        # Build messages for Claude (following Anthropic SDK pattern)
        messages = []

        # Add system prompt (Anthropic API uses separate system parameter)
        system_prompt = self._current_prompt if self._current_prompt else None

        # Add context if provided
        user_prompt = prompt
        if context:
            context_str = self._format_context(context)
            user_prompt = f"{context_str}\n\nTask: {prompt}"

        messages.append({"role": "user", "content": user_prompt})

        # Get response from Claude using Anthropic API
        try:
            # Use the LLM client which wraps Anthropic SDK
            # The client handles system message separately (as per Anthropic API)
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            response = self.llm_client.chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract code from response
            code, tests = self._extract_code_and_tests(response)

            return AgentOutput(
                code=code,
                tests=tests,
                traces=[{"type": "llm_response", "content": response}],
                metadata={
                    "model": self.model,
                    "temperature": self.temperature,
                    "provider": "anthropic",
                    "api": "messages",  # Anthropic Messages API
                },
                prompt_used=self._current_prompt,
            )
        except Exception as e:
            # Return error output
            return AgentOutput(
                code="",
                tests=None,
                traces=[{"type": "error", "error": str(e)}],
                metadata={"error": str(e)},
                prompt_used=self._current_prompt,
            )

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context for inclusion in prompt."""
        parts = []

        if "files" in context:
            parts.append("Files:")
            for file_path, content in context["files"].items():
                parts.append(f"\n{file_path}:\n{content}")

        if "workspace" in context:
            parts.append(f"\nWorkspace: {context['workspace']}")

        return "\n".join(parts)

    def _extract_code_and_tests(self, response: str) -> tuple[str, str | None]:
        """
        Extract code and tests from Claude response.

        Claude Code typically returns code in markdown code blocks. This method
        extracts Python code blocks and identifies test files/patterns.
        """
        import re

        code = ""
        tests = None

        # Find all code blocks (support various language tags)
        # Pattern matches: ```python, ```py, ```, etc.
        code_blocks = re.findall(r"```(?:python|py)?\n(.*?)```", response, re.DOTALL)

        if code_blocks:
            # First block is usually the main code
            code = code_blocks[0].strip()

            # Look for test files or test blocks
            # Pattern 1: Explicit test file mentions
            test_file_pattern = r"(?:test|tests?)[^`]*?\.py.*?```(?:python|py)?\n(.*?)```"
            # Pattern 2: Test function definitions
            test_function_pattern = r"def\s+test_.*?```(?:python|py)?\n(.*?)```"
            # Pattern 3: Test class definitions
            test_class_pattern = r"class\s+Test.*?```(?:python|py)?\n(.*?)```"

            test_patterns = [test_file_pattern, test_function_pattern, test_class_pattern]

            test_matches = []
            for pattern in test_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                if matches:
                    test_matches.extend(matches)

            if test_matches:
                tests = "\n\n".join(test_matches)

        # If no code blocks found, check if entire response is code
        if not code:
            # Check if response looks like code (no markdown, mostly code-like)
            if not response.strip().startswith("#") and "\n" in response:
                # Might be raw code without markdown
                code = response.strip()
            else:
                code = response

        return code, tests

    def get_prompt(self) -> str:
        """Get current Claude Code prompt."""
        return self._current_prompt or ""

    def update_prompt(self, new_prompt: str) -> None:
        """Update Claude Code prompt."""
        self._current_prompt = new_prompt

    def get_adapter_type(self) -> str:
        """Get adapter type identifier."""
        return "claude-code"
