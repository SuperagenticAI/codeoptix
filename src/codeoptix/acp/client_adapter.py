"""ACP Client Adapter for connecting to other agents via ACP.

This allows CodeOptiX to connect to other ACP-compatible agents (Claude Code, Codex, etc.)
and perform quality engineering on their outputs.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from acp import (
    PROTOCOL_VERSION,
    Client,
    RequestError,
    connect_to_agent,
    text_block,
)
from acp.core import ClientSideConnection
from acp.schema import (
    AgentMessageChunk,
    ClientCapabilities,
    CreateTerminalResponse,
    Implementation,
    ReadTextFileResponse,
    RequestPermissionResponse,
    WriteTextFileResponse,
)

from codeoptix.acp.code_extractor import extract_all_code, extract_code_from_text
from codeoptix.adapters.base import AgentAdapter, AgentOutput

logger = logging.getLogger(__name__)


class ACPClientAdapter(AgentAdapter):
    """Adapter for connecting to ACP-compatible agents."""

    def __init__(
        self,
        agent_command: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ):
        """Initialize ACP client adapter.

        Args:
            agent_command: Command to spawn the ACP agent (e.g., ["python", "agent.py"])
            cwd: Working directory for the agent
            env: Environment variables for the agent
        """
        self.agent_command = agent_command
        self.cwd = cwd or str(Path.cwd())
        self.env = env or {}
        self._connection: ClientSideConnection | None = None
        self._session_id: str | None = None

    async def _ensure_connected(self) -> None:
        """Ensure connection to ACP agent is established."""
        if self._connection is not None:
            return

        # Spawn agent process
        process = await asyncio.create_subprocess_exec(
            *self.agent_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=self.cwd,
            env={**self.env, **dict(asyncio.get_event_loop().get_environ())},
        )

        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Agent process does not expose stdio pipes")

        # Create client implementation
        client_impl = _ACPClientImpl()
        self._connection = connect_to_agent(client_impl, process.stdin, process.stdout)

        # Initialize connection
        await self._connection.initialize(
            protocol_version=PROTOCOL_VERSION,
            client_capabilities=ClientCapabilities(),
            client_info=Implementation(
                name="codeoptix",
                title="CodeOptiX",
                version="0.1.0",
            ),
        )

        # Create new session
        session = await self._connection.new_session(mcp_servers=[], cwd=self.cwd)
        self._session_id = session.session_id

    async def generate_code(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AgentOutput:
        """Generate code using the ACP agent.

        Args:
            prompt: The prompt for code generation
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            AgentOutput with generated code
        """
        await self._ensure_connected()

        if not self._connection or not self._session_id:
            raise RuntimeError("Not connected to ACP agent")

        # Send prompt to agent
        response = await self._connection.prompt(
            session_id=self._session_id,
            prompt=[text_block(prompt)],
        )

        # Extract code and messages from response
        code_blocks = []
        messages = []
        code_content = ""

        # Extract from response messages if available
        if hasattr(response, "messages") and response.messages:
            for message in response.messages:
                # Extract text content
                if hasattr(message, "content"):
                    content = message.content
                    if isinstance(content, str):
                        messages.append(content)
                        # Extract code from text
                        code_blocks.extend(extract_code_from_text(content))
                    elif hasattr(content, "text"):
                        text = getattr(content, "text", "")
                        if text:
                            messages.append(text)
                            code_blocks.extend(extract_code_from_text(text))

        # Extract from response updates if available
        if hasattr(response, "updates") and response.updates:
            code_blocks.extend(extract_all_code(response.updates))
            for update in response.updates:
                if hasattr(update, "content"):
                    content = update.content
                    if isinstance(content, str):
                        messages.append(content)
                    elif hasattr(content, "text"):
                        messages.append(getattr(content, "text", ""))

        # Combine all code blocks
        if code_blocks:
            # Prefer code blocks over inline code
            block_codes = [cb["content"] for cb in code_blocks if cb.get("type") == "block"]
            if block_codes:
                code_content = "\n\n".join(block_codes)
            else:
                # Fallback to inline code
                inline_codes = [cb["content"] for cb in code_blocks if cb.get("type") == "inline"]
                if inline_codes:
                    code_content = "\n".join(inline_codes)

        return AgentOutput(
            code=code_content,
            tests="",
            messages=messages,
            metadata={
                "acp_session_id": self._session_id,
                "stop_reason": response.stop_reason if hasattr(response, "stop_reason") else None,
                "code_blocks_count": len(code_blocks),
            },
        )

    async def close(self) -> None:
        """Close the ACP connection."""
        if self._connection:
            try:
                # Try to gracefully close the connection
                # Note: ACP doesn't have an explicit close method, but we can clean up
                if hasattr(self._connection, "close"):
                    await self._connection.close()
            except Exception as e:
                logger.warning(f"Error closing ACP connection: {e}")
            finally:
                self._connection = None
                self._session_id = None


class _ACPClientImpl(Client):
    """Internal client implementation for ACP adapter."""

    async def request_permission(
        self,
        options: list,
        session_id: str,
        tool_call: Any,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        """Handle permission requests."""
        # Auto-approve for now (can be made configurable)
        return RequestPermissionResponse(granted=True)

    async def write_text_file(
        self,
        content: str,
        path: str,
        session_id: str,
        **kwargs: Any,
    ) -> WriteTextFileResponse | None:
        """Handle file write requests."""
        # Allow file writes
        return WriteTextFileResponse()

    async def read_text_file(
        self,
        path: str,
        session_id: str,
        limit: int | None = None,
        line: int | None = None,
        **kwargs: Any,
    ) -> ReadTextFileResponse:
        """Handle file read requests."""
        try:
            with open(path, encoding="utf-8") as f:
                if line is not None:
                    lines = f.readlines()
                    if 0 <= line < len(lines):
                        content = lines[line]
                    else:
                        content = ""
                elif limit is not None:
                    content = f.read(limit)
                else:
                    content = f.read()
            return ReadTextFileResponse(content=content)
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            raise RequestError.internal_error(f"Failed to read file: {e}")

    async def create_terminal(
        self,
        command: str,
        session_id: str,
        args: list[str] | None = None,
        cwd: str | None = None,
        env: list | None = None,
        output_byte_limit: int | None = None,
        **kwargs: Any,
    ) -> CreateTerminalResponse:
        """Handle terminal creation requests."""
        raise RequestError.method_not_found("terminal/create")

    async def terminal_output(
        self,
        session_id: str,
        terminal_id: str,
        **kwargs: Any,
    ) -> Any:
        """Handle terminal output requests."""
        raise RequestError.method_not_found("terminal/output")

    async def release_terminal(
        self,
        session_id: str,
        terminal_id: str,
        **kwargs: Any,
    ) -> Any:
        """Handle terminal release requests."""
        raise RequestError.method_not_found("terminal/release")

    async def wait_for_terminal_exit(
        self,
        session_id: str,
        terminal_id: str,
        **kwargs: Any,
    ) -> Any:
        """Handle terminal exit wait requests."""
        raise RequestError.method_not_found("terminal/wait_for_exit")

    async def kill_terminal(
        self,
        session_id: str,
        terminal_id: str,
        **kwargs: Any,
    ) -> Any:
        """Handle terminal kill requests."""
        raise RequestError.method_not_found("terminal/kill")

    async def session_update(
        self,
        session_id: str,
        update: Any,
        **kwargs: Any,
    ) -> None:
        """Handle session updates from agent."""
        # Log updates for debugging
        if isinstance(update, AgentMessageChunk):
            logger.debug(f"Agent message: {update}")

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle extension methods."""
        raise RequestError.method_not_found(method)

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle extension notifications."""
        logger.debug(f"Extension notification: {method}")

    def on_connect(self, conn: Any) -> None:
        """Called when client connects to agent."""
        logger.debug("Connected to ACP agent")
