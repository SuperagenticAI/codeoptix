"""Gemini CLI adapter for CodeOptix.

This adapter interfaces with Google Gemini CLI, which uses the Google Generative AI
SDK for agent-based code generation and execution. The adapter executes the CLI via
subprocess in non-interactive mode and parses JSON output.

Note: Gemini CLI is a full CLI tool that executes code and uses tools. This adapter
provides a simplified interface for CodeOptix's evaluation framework.
"""

import json
import os
import subprocess
from typing import Any

from codeoptix.adapters.base import AgentAdapter, AgentOutput


class GeminiCLIAdapter(AgentAdapter):
    """
    Adapter for Google Gemini CLI.

    Gemini CLI is a coding agent that uses Google's Generative AI SDK. This adapter
    executes Gemini CLI via subprocess in non-interactive mode with JSON output
    to capture structured responses from the agent.

    The adapter uses `gemini` command in non-interactive mode with JSON output
    to capture the agent's responses, code generation, and tool execution.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize Gemini CLI adapter."""
        super().__init__(config)

        # Get LLM configuration
        llm_config = config.get("llm_config", {})
        self.api_key = (
            llm_config.get("api_key") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        )
        self.model = llm_config.get("model", "gemini-2.0-flash-exp")

        # Gemini CLI path (defaults to system PATH)
        self.gemini_path = config.get("gemini_path") or self._find_gemini_path()

        # Working directory for Gemini execution
        self.working_directory = config.get("working_directory") or os.getcwd()

        # Output format (json or stream-json)
        self.output_format = config.get("output_format", "json")

        # Get initial prompt if provided
        self._current_prompt = config.get("prompt") or self._get_default_prompt()

    def _find_gemini_path(self) -> str:
        """Find Gemini CLI executable path."""
        # First check if gemini is in PATH
        import shutil

        gemini_path = shutil.which("gemini")
        if gemini_path:
            return gemini_path

        # Fallback: try common installation locations
        possible_paths = [
            os.path.expanduser("~/.local/bin/gemini"),
            "/usr/local/bin/gemini",
            "/opt/homebrew/bin/gemini",  # macOS Homebrew
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # If not found, return "gemini" and let subprocess handle the error
        return "gemini"

    def _get_default_prompt(self) -> str:
        """Get default Gemini CLI system prompt."""
        return """You are a helpful coding assistant. Write clean, secure, and well-tested code.
Follow best practices:
- Write secure code (no hardcoded secrets, validate inputs)
- Write meaningful tests
- Follow the user's requirements"""

    def execute(self, prompt: str, context: dict[str, Any] | None = None) -> AgentOutput:
        """
        Execute Gemini CLI with a task prompt.

        Uses `gemini` command in non-interactive mode with JSON output to capture
        the agent's responses, code generation, and tool execution.
        """
        context = context or {}

        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)

        # Execute Gemini CLI
        try:
            result = self._execute_gemini_cli(full_prompt)

            # Parse JSON output to extract code and tests
            code, tests = self._extract_from_json(result)

            return AgentOutput(
                code=code,
                tests=tests,
                traces=result.get("traces", []),
                metadata={
                    "model": self.model,
                    "provider": "google",
                    "gemini_version": result.get("gemini_version"),
                    "stats": result.get("stats"),
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

    def _execute_gemini_cli(self, prompt: str) -> dict[str, Any]:
        """
        Execute Gemini CLI via subprocess and parse JSON output.

        Uses `gemini` command with `--json` or `--stream-json` flag to get
        structured output in non-interactive mode.
        """
        # Build command arguments
        cmd = [self.gemini_path]

        # Add output format (--output-format json or --output-format stream-json)
        output_format = "stream-json" if self.output_format == "stream-json" else "json"
        cmd.extend(["--output-format", output_format])

        # Add model if specified
        if self.model:
            cmd.extend(["--model", self.model])

        # Set up environment
        env = os.environ.copy()
        if self.api_key:
            env["GOOGLE_API_KEY"] = self.api_key
            env["GEMINI_API_KEY"] = self.api_key

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
                raise RuntimeError(f"Gemini CLI exited with code {process.returncode}: {stderr}")

            # Parse JSON output
            return self._parse_json_output(stdout, stderr)

        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError("Gemini CLI execution timed out after 300 seconds")
        except FileNotFoundError:
            raise RuntimeError(
                f"Gemini CLI not found at '{self.gemini_path}'. "
                "Please install Gemini CLI: npm install -g @google/gemini-cli"
            )

    def _parse_json_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse JSON output from Gemini CLI.

        Gemini CLI outputs JSON in the following formats:
        - JSON: Single JSON object with session_id, content, stats
        - Stream JSON: JSON Lines (JSONL) with events (INIT, MESSAGE, TOOL_USE, TOOL_RESULT, RESULT)
        """
        traces = []
        content = ""
        stats = None
        tool_calls = []

        # Try to parse as single JSON object first
        try:
            data = json.loads(stdout.strip())

            # Standard JSON format
            if "content" in data:
                content = data.get("content", "")
                stats = data.get("stats")
                traces.append({"type": "json_response", "data": data})

            return {
                "traces": traces,
                "content": content,
                "stats": stats,
                "tool_calls": tool_calls,
                "stderr": stderr,
            }
        except json.JSONDecodeError:
            # Try parsing as JSONL (stream-json format)
            pass

        # Parse as JSONL (stream-json format)
        for line in stdout.strip().split("\n"):
            if not line.strip():
                continue

            try:
                event = json.loads(line)
                event_type = event.get("type", "")

                traces.append(event)

                if event_type == "MESSAGE":
                    # Accumulate message content
                    if event.get("role") == "assistant":
                        content += event.get("content", "")

                elif event_type == "TOOL_USE":
                    tool_calls.append(
                        {
                            "tool_name": event.get("tool_name"),
                            "tool_id": event.get("tool_id"),
                            "parameters": event.get("parameters"),
                        }
                    )

                elif event_type == "TOOL_RESULT":
                    # Tool execution result
                    tool_calls.append(
                        {
                            "tool_id": event.get("tool_id"),
                            "status": event.get("status"),
                            "output": event.get("output"),
                            "error": event.get("error"),
                        }
                    )

                elif event_type == "RESULT":
                    stats = event.get("stats")

            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue

        return {
            "traces": traces,
            "content": content,
            "stats": stats,
            "tool_calls": tool_calls,
            "stderr": stderr,
        }

    def _extract_from_json(self, result: dict[str, Any]) -> tuple[str, str | None]:
        """
        Extract code and tests from Gemini JSON output.

        Looks for:
        - Code in markdown code blocks in message content
        - Tool calls that create/modify files (file_write, file_edit tools)
        - Test files in tool results
        """
        content = result.get("content", "")
        tool_calls = result.get("tool_calls", [])
        code = ""
        tests = None

        # Extract code from message content (markdown code blocks)
        import re

        code_blocks = re.findall(
            r"```(?:python|javascript|typescript)?\n(.*?)```", content, re.DOTALL
        )
        if code_blocks:
            code = code_blocks[0].strip()

        # Look for file operations in tool calls
        code_files = []
        test_files = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name", "")
            parameters = tool_call.get("parameters", {})
            output = tool_call.get("output", "")

            # Check for file write/edit operations
            if tool_name in ["file_write", "file_edit", "write_file"]:
                file_path = parameters.get("path") or parameters.get("file_path", "")
                file_content = parameters.get("content") or parameters.get("file_content", "")

                if file_path.endswith((".py", ".js", ".ts")):
                    if "test" in file_path.lower() or "test_" in file_path:
                        test_files.append((file_path, file_content))
                    else:
                        code_files.append((file_path, file_content))

            # Check tool results for file content
            if output and isinstance(output, str):
                # Try to extract file paths and content from output
                file_matches = re.findall(
                    r"File:\s*([^\n]+)\n```[^\n]*\n(.*?)```", output, re.DOTALL
                )
                for file_path, file_content in file_matches:
                    if file_path.endswith((".py", ".js", ".ts")):
                        if "test" in file_path.lower():
                            test_files.append((file_path, file_content))
                        else:
                            code_files.append((file_path, file_content))

        # Use file operations if available, otherwise use extracted code
        if code_files:
            # Combine all code files
            code = "\n\n".join(f"# {path}\n{content}" for path, content in code_files)
        elif not code:
            # Fallback to message content
            code = content

        # Extract tests
        if test_files:
            tests = "\n\n".join(f"# {path}\n{content}" for path, content in test_files)

        return code, tests

    def get_prompt(self) -> str:
        """Get current Gemini CLI prompt."""
        return self._current_prompt or ""

    def update_prompt(self, new_prompt: str) -> None:
        """Update Gemini CLI prompt."""
        self._current_prompt = new_prompt

    def get_adapter_type(self) -> str:
        """Get adapter type identifier."""
        return "gemini-cli"
