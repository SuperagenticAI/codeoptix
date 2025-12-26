"""ACP Agent Registry - Manage and connect to multiple ACP-compatible agents."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from acp import PROTOCOL_VERSION, Client, connect_to_agent
from acp.core import ClientSideConnection
from acp.schema import (
    ClientCapabilities,
    CreateTerminalResponse,
    Implementation,
    ReadTextFileResponse,
    RequestPermissionResponse,
    WriteTextFileResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class ACPAgentConfig:
    """Configuration for an ACP agent."""

    name: str
    command: list[str]
    cwd: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    description: str = ""
    capabilities: list[str] = field(default_factory=list)


class ACPAgentRegistry:
    """Registry for managing ACP-compatible agents."""

    def __init__(self):
        """Initialize the agent registry."""
        self._agents: dict[str, ACPAgentConfig] = {}
        self._connections: dict[str, ClientSideConnection] = {}
        self._sessions: dict[str, str] = {}  # agent_name -> session_id

    def register(
        self,
        name: str,
        command: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        description: str = "",
        capabilities: list[str] | None = None,
    ) -> None:
        """Register an ACP agent.

        Args:
            name: Unique name for the agent
            command: Command to spawn the agent (e.g., ["python", "agent.py"])
            cwd: Working directory for the agent
            env: Environment variables
            description: Description of the agent
            capabilities: List of agent capabilities
        """
        config = ACPAgentConfig(
            name=name,
            command=command,
            cwd=cwd,
            env=env or {},
            description=description,
            capabilities=capabilities or [],
        )
        self._agents[name] = config
        logger.info(f"Registered ACP agent: {name}")

    def unregister(self, name: str) -> None:
        """Unregister an ACP agent.

        Args:
            name: Name of the agent to unregister
        """
        if name in self._agents:
            # Close connection if open
            if name in self._connections:
                self._connections.pop(name)
            if name in self._sessions:
                self._sessions.pop(name)
            del self._agents[name]
            logger.info(f"Unregistered ACP agent: {name}")

    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(self._agents.keys())

    def get_agent(self, name: str) -> ACPAgentConfig | None:
        """Get agent configuration.

        Args:
            name: Agent name

        Returns:
            Agent configuration or None if not found
        """
        return self._agents.get(name)

    async def connect(self, name: str) -> ClientSideConnection:
        """Connect to a registered ACP agent.

        Args:
            name: Agent name

        Returns:
            ClientSideConnection to the agent

        Raises:
            ValueError: If agent not found
            RuntimeError: If connection fails
        """
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not found in registry")

        # Return existing connection if available
        if name in self._connections:
            return self._connections[name]

        config = self._agents[name]

        # Spawn agent process
        process = await asyncio.create_subprocess_exec(
            *config.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=config.cwd,
            env={**config.env, **dict(asyncio.get_event_loop().get_environ())},
        )

        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Agent process does not expose stdio pipes")

        # Create client implementation
        client_impl = _RegistryClientImpl()
        connection = connect_to_agent(client_impl, process.stdin, process.stdout)

        # Initialize connection
        await connection.initialize(
            protocol_version=PROTOCOL_VERSION,
            client_capabilities=ClientCapabilities(),
            client_info=Implementation(
                name="codeoptix-registry",
                title="CodeOptiX Agent Registry",
                version="0.1.0",
            ),
        )

        # Create new session
        session = await connection.new_session(mcp_servers=[], cwd=config.cwd or ".")
        self._sessions[name] = session.session_id

        # Store connection
        self._connections[name] = connection

        logger.info(f"Connected to ACP agent: {name}")
        return connection

    async def disconnect(self, name: str) -> None:
        """Disconnect from an agent.

        Args:
            name: Agent name
        """
        if name in self._connections:
            connection = self._connections[name]
            try:
                # Try to gracefully close the connection
                if hasattr(connection, "close"):
                    await connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection to agent {name}: {e}")
            finally:
                self._connections.pop(name)
        if name in self._sessions:
            self._sessions.pop(name)
        logger.info(f"Disconnected from ACP agent: {name}")

    def get_session_id(self, name: str) -> str | None:
        """Get session ID for an agent.

        Args:
            name: Agent name

        Returns:
            Session ID or None if not connected
        """
        return self._sessions.get(name)


class _RegistryClientImpl(Client):
    """Internal client implementation for registry connections."""

    async def request_permission(
        self,
        options: list,
        session_id: str,
        tool_call: Any,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        """Handle permission requests."""
        return RequestPermissionResponse(granted=True)

    async def write_text_file(
        self,
        content: str,
        path: str,
        session_id: str,
        **kwargs: Any,
    ) -> WriteTextFileResponse | None:
        """Handle file write requests."""
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
            raise

    async def create_terminal(self, *args: Any, **kwargs: Any) -> CreateTerminalResponse:
        """Handle terminal creation."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found("terminal/create")

    async def terminal_output(self, *args: Any, **kwargs: Any) -> Any:
        """Handle terminal output."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found("terminal/output")

    async def release_terminal(self, *args: Any, **kwargs: Any) -> Any:
        """Handle terminal release."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found("terminal/release")

    async def wait_for_terminal_exit(self, *args: Any, **kwargs: Any) -> Any:
        """Handle terminal exit wait."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found("terminal/wait_for_exit")

    async def kill_terminal(self, *args: Any, **kwargs: Any) -> Any:
        """Handle terminal kill."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found("terminal/kill")

    async def session_update(
        self,
        session_id: str,
        update: Any,
        **kwargs: Any,
    ) -> None:
        """Handle session updates from agent."""
        # Registry doesn't need to handle updates

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle extension methods."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found(method)

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle extension notifications."""
        logger.debug(f"Extension notification: {method}")

    def on_connect(self, conn: Any) -> None:
        """Called when client connects to agent."""
        logger.debug("Registry connected to ACP agent")
