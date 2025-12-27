"""Basic agent adapter for testing and simple use cases."""

from typing import Any

from codeoptix.adapters.base import AgentAdapter, AgentOutput
from codeoptix.utils.llm import LLMClient


class BasicAdapter(AgentAdapter):
    """
    Basic agent adapter that works with any LLM provider.

    This adapter doesn't require any external agent software and can be used
    for testing or simple evaluation scenarios. It uses the LLM directly
    with a simple coding assistant prompt.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize basic adapter."""
        super().__init__(config)

        # Get LLM configuration
        llm_config = config.get("llm_config", {})
        if not llm_config:
            raise ValueError("BasicAdapter requires 'llm_config' in configuration")

        # Create LLM client
        from codeoptix.utils.llm import LLMProvider, create_llm_client

        provider_name = llm_config.get("provider", "ollama")
        self.llm_client: LLMClient = create_llm_client(
            LLMProvider(provider_name), llm_config.get("api_key"), llm_config.get("model")
        )

        # Set model
        self.model = llm_config.get("model", "llama3.2:3b")

        # Set default prompt
        self._current_prompt = config.get("prompt") or self._get_default_prompt()

    def get_adapter_type(self) -> str:
        """Get adapter type."""
        return "basic"

    def _get_default_prompt(self) -> str:
        """Get default basic coding assistant prompt."""
        return """You are a helpful coding assistant. Your task is to write clean, secure, and well-tested code.

Guidelines:
- Write secure code: validate inputs, avoid hardcoded secrets, use proper error handling
- Write comprehensive tests: cover edge cases, use meaningful assertions
- Follow coding best practices: clear variable names, proper structure, documentation
- Consider the user's requirements and context provided

When given a coding task, provide:
1. Well-structured, readable code
2. Appropriate tests for the code
3. Brief explanation of the implementation"""

    def get_prompt(self) -> str:
        """Get current system prompt."""
        return self._current_prompt or self._get_default_prompt()

    def update_prompt(self, new_prompt: str) -> None:
        """Update the system prompt."""
        self._current_prompt = new_prompt

    def execute(self, prompt: str, context: dict[str, Any] | None = None) -> "AgentOutput":
        """
        Execute a coding task using the LLM directly.

        Args:
            prompt: The coding task prompt
            context: Optional context information

        Returns:
            AgentOutput with generated code and tests
        """
        from codeoptix.adapters.base import AgentOutput

        context = context or {}

        # Build the full prompt
        full_prompt = self._build_full_prompt(prompt, context)

        # Get response from LLM
        messages = [
            {"role": "system", "content": self._current_prompt},
            {"role": "user", "content": full_prompt},
        ]

        response = self.llm_client.chat_completion(
            messages=messages, model=self.model, temperature=0.7, max_tokens=2048
        )

        # Parse the response into code and tests
        code, tests = self._parse_response(response)

        return AgentOutput(
            code=code,
            tests=tests,
            prompt_used=self._current_prompt,
            metadata={"model": self.model, "adapter_type": "basic", "full_response": response},
        )

    def _build_full_prompt(self, prompt: str, context: dict[str, Any]) -> str:
        """Build the full prompt including context."""
        parts = []

        # Add context if provided
        if context.get("plan"):
            parts.append(f"Plan/Requirements: {context['plan']}")
        if context.get("existing_code"):
            parts.append(f"Existing Code:\n{context['existing_code']}")
        if context.get("requirements"):
            parts.append(f"Requirements: {context['requirements']}")

        # Add the main task
        parts.append(f"Task: {prompt}")

        # Add output format instructions
        parts.append("""
Please provide your response in the following format:

CODE:
```python
# Your code here - must be valid Python
```

TESTS:
```python
# Your tests here - must be valid Python
```

EXPLANATION:
Brief explanation of your implementation.
""")

        return "\n\n".join(parts)

    def _parse_response(self, response: str) -> tuple[str, str]:
        """Parse LLM response into code and tests."""
        code = ""
        tests = ""

        # Simple parsing - look for CODE and TESTS sections
        lines = response.split("\n")
        current_section = None
        code_lines = []
        test_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            if line_lower.startswith("code:") or "```" in line_lower:
                current_section = "code"
                continue
            if line_lower.startswith(("tests:", "test:")):
                current_section = "tests"
                continue
            if current_section == "code" and line.strip():
                # Remove markdown code blocks
                if "```" in line:
                    continue
                code_lines.append(line)
            elif current_section == "tests" and line.strip():
                # Remove markdown code blocks
                if "```" in line:
                    continue
                test_lines.append(line)

        # If no clear sections found, try to extract from the whole response
        if not code_lines and not test_lines:
            # Look for function definitions for code
            # Look for test functions for tests
            for line in lines:
                if line.strip().startswith("def ") and "test" in line.lower():
                    current_section = "tests"
                    test_lines.append(line)
                elif line.strip().startswith("def ") and current_section != "tests":
                    current_section = "code"
                    code_lines.append(line)
                elif current_section == "code":
                    code_lines.append(line)
                elif current_section == "tests":
                    test_lines.append(line)

        code = "\n".join(code_lines).strip()
        tests = "\n".join(test_lines).strip()

        # Fallback if parsing failed
        if not code and not tests:
            # Assume the entire response is code
            code = response.strip()

        return code, tests
