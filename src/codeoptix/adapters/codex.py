"""Codex (OpenAI) adapter for CodeOptix.

This adapter interfaces with OpenAI Codex CLI, which uses the Responses API
for agent-based code generation and execution. The adapter follows the pattern
used in the official Codex TypeScript SDK, executing the CLI via subprocess
and parsing JSONL output.

Note: Codex is a full CLI tool that executes code in sandboxes. This adapter
provides a simplified interface for CodeOptix's evaluation framework.
"""

import json
import os
import subprocess
from typing import Any

from codeoptix.adapters.base import AgentAdapter, AgentOutput


class CodexAdapter(AgentAdapter):
    """
    Adapter for OpenAI Codex CLI.

    Codex is a coding agent that uses OpenAI's Responses API. This adapter
    executes Codex via the CLI (similar to the TypeScript SDK) and extracts
    code and test outputs from the agent's responses.

    The adapter uses `codex exec` in non-interactive mode with JSON output
    to capture structured responses from the agent.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize Codex adapter."""
        super().__init__(config)

        # Get LLM configuration
        llm_config = config.get("llm_config", {})
        self.api_key = (
            llm_config.get("api_key") or os.getenv("OPENAI_API_KEY") or os.getenv("CODEX_API_KEY")
        )
        self.model = llm_config.get("model", "gpt-4o")
        self.base_url = llm_config.get("base_url")

        # Codex CLI path (defaults to system PATH)
        self.codex_path = config.get("codex_path") or self._find_codex_path()

        # Working directory for Codex execution
        self.working_directory = config.get("working_directory") or os.getcwd()

        # Sandbox mode (read-only by default for safety)
        self.sandbox_mode = config.get("sandbox_mode", "read-only")

        # Get initial prompt if provided
        self._current_prompt = config.get("prompt") or self._get_default_prompt()

    def _find_codex_path(self) -> str:
        """Find Codex CLI executable path."""
        # First check if codex is in PATH
        import shutil

        codex_path = shutil.which("codex")
        if codex_path:
            return codex_path

        # Fallback: try common installation locations
        possible_paths = [
            os.path.expanduser("~/.local/bin/codex"),
            "/usr/local/bin/codex",
            "/opt/homebrew/bin/codex",  # macOS Homebrew
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # If not found, return "codex" and let subprocess handle the error
        return "codex"

    def _get_default_prompt(self) -> str:
        """Get default Codex system prompt."""
        return """You are an expert Python programmer. Write clean, secure, and well-tested code.
Best practices:
- No hardcoded secrets or credentials
- Write comprehensive tests
- Follow specifications exactly"""

    def execute(self, prompt: str, context: dict[str, Any] | None = None) -> AgentOutput:
        """
        Execute Codex with a task prompt.

        Uses `codex exec` in non-interactive mode with JSON output to capture
        the agent's responses, code generation, and test execution.
        """
        context = context or {}

        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)

        # Execute Codex CLI
        try:
            result = self._execute_codex_cli(full_prompt)

            # Parse JSONL output to extract code and tests
            code, tests = self._extract_from_jsonl(result)

            return AgentOutput(
                code=code,
                tests=tests,
                traces=result.get("traces", []),
                metadata={
                    "model": self.model,
                    "provider": "openai",
                    "codex_version": result.get("codex_version"),
                    "usage": result.get("usage"),
                },
                prompt_used=self._current_prompt,
            )
        except Exception as e:
            return AgentOutput(
                code="",
                tests=None,
                traces=[{"type": "error", "error": str(e)}],
                metadata={"error": str(e)},
                prompt_used=self._current_prompt,
            )

    def _build_prompt(self, prompt: str, context: dict[str, Any]) -> str:
        """Build the full prompt including system instructions and context."""
        parts = []

        # Add system prompt if available
        if self._current_prompt:
            parts.append(f"System instructions: {self._current_prompt}\n")

        # Add context
        if context:
            if "plan" in context:
                parts.append(f"Plan: {context['plan']}\n")
            if "requirements" in context:
                reqs = context["requirements"]
                if isinstance(reqs, list):
                    reqs = "\n".join(f"- {r}" for r in reqs)
                parts.append(f"Requirements:\n{reqs}\n")
            if "files" in context:
                parts.append("Files:")
                for file_path, content in context["files"].items():
                    parts.append(f"\n{file_path}:\n{content}")

        # Add the main task
        parts.append(f"\nTask: {prompt}")

        return "\n".join(parts)

    def _execute_codex_cli(self, prompt: str) -> dict[str, Any]:
        """
        Execute Codex CLI via subprocess and parse JSONL output.

        This follows the pattern from the TypeScript SDK, using `codex exec`
        with `--experimental-json` flag to get structured output.
        """
        # Build command arguments
        cmd = [self.codex_path, "exec", "--experimental-json"]

        # Add model if specified
        if self.model:
            cmd.extend(["--model", self.model])

        # Add sandbox mode
        if self.sandbox_mode:
            cmd.extend(["--sandbox", self.sandbox_mode])

        # Add working directory
        if self.working_directory:
            cmd.extend(["--cd", self.working_directory])

        # Skip git repo check for evaluation contexts
        cmd.append("--skip-git-repo-check")

        # Set up environment
        env = os.environ.copy()
        if self.api_key:
            env["CODEX_API_KEY"] = self.api_key
        if self.base_url:
            env["OPENAI_BASE_URL"] = self.base_url

        # Execute and capture output
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self.working_directory,
            )

            stdout, stderr = process.communicate(input=prompt, timeout=300)

            if process.returncode != 0:
                raise RuntimeError(f"Codex CLI exited with code {process.returncode}: {stderr}")

            # Parse JSONL output
            return self._parse_jsonl_output(stdout, stderr)

        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError("Codex CLI execution timed out after 300 seconds")
        except FileNotFoundError:
            raise RuntimeError(
                f"Codex CLI not found at '{self.codex_path}'. "
                "Please install Codex CLI: npm install -g @openai/codex"
            )

    def _parse_jsonl_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse JSONL output from Codex CLI.

        Codex outputs events as JSON Lines (JSONL), including:
        - thread.started
        - turn.started/turn.completed
        - item.completed (agent_message, command_execution, file_change, etc.)
        """
        traces = []
        items = []
        usage = None
        final_message = None

        # Parse each JSON line
        for line in stdout.strip().split("\n"):
            if not line.strip():
                continue

            try:
                event = json.loads(line)
                event_type = event.get("type", "")

                traces.append(event)

                if event_type == "turn.completed":
                    usage = event.get("usage")
                elif event_type == "item.completed":
                    item = event.get("item", {})
                    items.append(item)

                    # Extract final agent message
                    if item.get("type") == "agent_message":
                        final_message = item.get("text", "")

            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue

        return {
            "traces": traces,
            "items": items,
            "usage": usage,
            "final_message": final_message,
            "stderr": stderr,
        }

    def _extract_from_jsonl(self, result: dict[str, Any]) -> tuple[str, str | None]:
        """
        Extract code and tests from Codex JSONL output.

        Looks for:
        - file_change items (code files created/modified)
        - command_execution items (test runs)
        - agent_message items (code in markdown blocks)
        """
        items = result.get("items", [])
        code = ""
        tests = None

        # Look for file changes (code files)
        code_files = []
        test_files = []

        for item in items:
            item_type = item.get("type")

            if item_type == "file_change":
                file_path = item.get("file_path", "")
                content = item.get("content", "")

                if file_path.endswith(".py"):
                    if "test" in file_path.lower() or "test_" in file_path:
                        test_files.append((file_path, content))
                    else:
                        code_files.append((file_path, content))

            elif item_type == "agent_message":
                # Extract code from markdown code blocks in messages
                text = item.get("text", "")
                import re

                code_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
                if code_blocks:
                    code = code_blocks[0].strip()

        # Use file changes if available, otherwise use extracted code
        if code_files:
            # Combine all code files
            code = "\n\n".join(f"# {path}\n{content}" for path, content in code_files)
        elif not code:
            # Fallback to final message
            final_message = result.get("final_message", "")
            if final_message:
                code = final_message

        # Extract tests
        if test_files:
            tests = "\n\n".join(f"# {path}\n{content}" for path, content in test_files)

        return code, tests

    def get_prompt(self) -> str:
        """Get current Codex prompt."""
        return self._current_prompt or ""

    def update_prompt(self, new_prompt: str) -> None:
        """Update Codex prompt."""
        self._current_prompt = new_prompt

    def get_adapter_type(self) -> str:
        """Get adapter type identifier."""
        return "codex"
