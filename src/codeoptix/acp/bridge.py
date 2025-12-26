"""ACP Quality Bridge - CodeOptiX as quality middleware between editor and agents.

This implements the "Quality Bridge" pattern where CodeOptiX sits between
the editor and coding agents, automatically performing quality checks.
"""

import asyncio
import logging
from typing import Any

from acp import PROTOCOL_VERSION, Client, connect_to_agent, text_block, update_agent_message
from acp.core import ClientSideConnection
from acp.schema import (
    AgentMessageChunk,
    ClientCapabilities,
    Implementation,
    TextContentBlock,
)

from codeoptix.acp.code_extractor import extract_all_code, extract_code_from_message
from codeoptix.acp.registry import ACPAgentRegistry
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMClient

logger = logging.getLogger(__name__)


class ACPQualityBridge:
    """CodeOptiX as a quality bridge between editor and agents via ACP."""

    def __init__(
        self,
        agent_command: list[str] | None = None,
        agent_name: str | None = None,
        evaluation_engine: EvaluationEngine | None = None,
        llm_client: LLMClient | None = None,
        auto_eval: bool = True,
        registry: ACPAgentRegistry | None = None,
        behaviors: list[str] | None = None,
    ):
        """Initialize ACP quality bridge.

        Args:
            agent_command: Command to spawn the ACP agent (e.g., ["python", "agent.py"])
            agent_name: Name of agent in registry (alternative to agent_command)
            evaluation_engine: Optional evaluation engine
            llm_client: Optional LLM client
            auto_eval: Whether to automatically evaluate code quality
            registry: Optional agent registry (for multi-agent support)
            behaviors: List of behavior names to evaluate (default: all)
        """
        if not agent_command and not agent_name:
            raise ValueError("Either agent_command or agent_name must be provided")

        self.agent_command = agent_command
        self.agent_name = agent_name
        self.evaluation_engine = evaluation_engine
        self.llm_client = llm_client
        self.auto_eval = auto_eval
        self.registry = registry
        self.behaviors = behaviors or ["insecure-code", "vacuous-tests", "plan-drift"]
        self._connection: ClientSideConnection | None = None
        self._session_id: str | None = None
        self._collected_updates: list[Any] = []  # Collect updates for code extraction

    async def connect(self, cwd: str | None = None) -> None:
        """Connect to the ACP agent."""
        if self.agent_name and self.registry:
            # Use registry to connect
            self._connection = await self.registry.connect(self.agent_name)
            self._session_id = self.registry.get_session_id(self.agent_name)
        elif self.agent_command:
            # Spawn agent process directly
            process = await asyncio.create_subprocess_exec(
                *self.agent_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            if process.stdin is None or process.stdout is None:
                raise RuntimeError("Agent process does not expose stdio pipes")

            # Create bridge client implementation
            client_impl = _BridgeClientImpl(self)
            self._connection = connect_to_agent(client_impl, process.stdin, process.stdout)

            # Initialize connection
            await self._connection.initialize(
                protocol_version=PROTOCOL_VERSION,
                client_capabilities=ClientCapabilities(),
                client_info=Implementation(
                    name="codeoptix-bridge",
                    title="CodeOptiX Quality Bridge",
                    version="0.1.0",
                ),
            )

            # Create new session
            session = await self._connection.new_session(mcp_servers=[], cwd=cwd or ".")
            self._session_id = session.session_id
        else:
            raise RuntimeError("No agent command or registry agent name provided")

    async def prompt(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Send a prompt through the quality bridge."""
        if not self._connection or not self._session_id:
            raise RuntimeError("Not connected to ACP agent")

        # Clear collected updates
        self._collected_updates = []

        # Send prompt to agent
        response = await self._connection.prompt(
            session_id=self._session_id,
            prompt=[text_block(prompt)],
        )

        # Perform quality evaluation on response
        if self.auto_eval and self.evaluation_engine and self._collected_updates:
            await self._evaluate_and_feedback()

        return response.stop_reason or "end_turn"

    async def _evaluate_and_feedback(self) -> None:
        """Evaluate collected code and send feedback to editor."""
        if not self._connection or not self._session_id:
            return

        # Extract code from collected updates
        code_blocks = extract_all_code(self._collected_updates)

        if not code_blocks:
            logger.debug("No code blocks found in agent response")
            return

        # Send evaluation status
        await self._connection.session_update(
            session_id=self._session_id,
            update=update_agent_message(text_block("🔍 CodeOptiX: Evaluating code quality...")),
            source="codeoptix",
        )

        try:
            # Evaluate each code block
            all_results = []
            for code_block in code_blocks:
                code_content = code_block.get("content", "")
                if not code_content:
                    continue

                # Evaluate code block (synchronous)
                results = self.bridge._evaluate_code_block(code_content, code_block)

                all_results.append(
                    {
                        "code_block": code_block,
                        "results": results,
                    }
                )

            # Format and send feedback
            feedback = self._format_quality_feedback(all_results)
            await self._connection.session_update(
                session_id=self._session_id,
                update=update_agent_message(text_block(feedback)),
                source="codeoptix",
            )

        except Exception as e:
            logger.error(f"Error during quality evaluation: {e}")
            await self._connection.session_update(
                session_id=self._session_id,
                update=update_agent_message(text_block(f"⚠️ CodeOptiX: Evaluation error: {e!s}")),
                source="codeoptix",
            )

    def _format_quality_feedback(self, results: list[dict[str, Any]]) -> str:
        """Format quality evaluation results for display.

        Args:
            results: List of evaluation results

        Returns:
            Formatted feedback string
        """
        lines = ["## 🔍 CodeOptiX Quality Report\n"]

        for i, result_data in enumerate(results, 1):
            code_block = result_data["code_block"]
            results_dict = result_data["results"]

            lines.append(f"### Code Block {i} ({code_block.get('language', 'text')})\n")

            if "behaviors" in results_dict:
                for behavior_name, behavior_data in results_dict["behaviors"].items():
                    passed = behavior_data.get("passed", True)
                    score = behavior_data.get("score", 0.0)
                    emoji = "✅" if passed else "❌"

                    lines.append(f"{emoji} **{behavior_name}**: {score:.2%}")

                    if not passed and behavior_data.get("evidence"):
                        evidence = behavior_data["evidence"][:2]  # Limit to 2 items
                        for ev in evidence:
                            lines.append(f"   - {ev}")

            lines.append("")

        return "\n".join(lines)

    async def close(self) -> None:
        """Close the bridge connection."""
        if self._connection:
            self._connection = None
            self._session_id = None


class _BridgeClientImpl(Client):
    """Internal client implementation for quality bridge."""

    def __init__(self, bridge: ACPQualityBridge):
        """Initialize bridge client."""
        self.bridge = bridge

    async def request_permission(
        self,
        options: list,
        session_id: str,
        tool_call: Any,
        **kwargs: Any,
    ) -> Any:
        """Handle permission requests."""
        # Auto-approve for bridge
        from acp.schema import RequestPermissionResponse

        return RequestPermissionResponse(granted=True)

    async def write_text_file(
        self,
        content: str,
        path: str,
        session_id: str,
        **kwargs: Any,
    ) -> Any:
        """Handle file write requests."""
        # Allow file writes, but could add quality checks here
        from acp.schema import WriteTextFileResponse

        return WriteTextFileResponse()

    async def read_text_file(
        self,
        path: str,
        session_id: str,
        limit: int | None = None,
        line: int | None = None,
        **kwargs: Any,
    ) -> Any:
        """Handle file read requests."""
        from acp.schema import ReadTextFileResponse

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

    async def create_terminal(self, *args: Any, **kwargs: Any) -> Any:
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
        # Collect updates for code extraction and evaluation
        self._collected_updates.append(update)

        # Intercept agent messages for quality evaluation
        if isinstance(update, AgentMessageChunk):
            content = update.content
            if isinstance(content, TextContentBlock):
                logger.debug(f"Agent message: {content.text[:100]}...")

                # Extract code immediately for real-time feedback
                if self.bridge.auto_eval and self.bridge.evaluation_engine:
                    code_blocks = extract_code_from_message(update)
                    if code_blocks:
                        # Quick evaluation for real-time feedback
                        await self.bridge._quick_evaluate_code(code_blocks, session_id)

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle extension methods."""
        from acp.exceptions import RequestError

        raise RequestError.method_not_found(method)

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        """Handle extension notifications."""
        logger.debug(f"Extension notification: {method}")

    def _evaluate_code_block(self, code_content: str, code_block: dict[str, str]) -> dict[str, Any]:
        """Evaluate a single code block.

        Args:
            code_content: Code content to evaluate
            code_block: Code block metadata

        Returns:
            Evaluation results dictionary
        """
        if not self.evaluation_engine:
            return {}

        # Use evaluation engine's evaluate_behaviors (synchronous)
        try:
            results = self.evaluation_engine.evaluate_behaviors(
                behavior_names=self.behaviors,
                context={"code": code_content, "source": "acp_bridge", "code_block": code_block},
            )
            return results
        except Exception as e:
            logger.error(f"Error in code block evaluation: {e}")
            return {"error": str(e)}

    async def _quick_evaluate_code(
        self, code_blocks: list[dict[str, str]], session_id: str
    ) -> None:
        """Perform quick evaluation on code blocks for real-time feedback.

        Args:
            code_blocks: List of extracted code blocks
            session_id: ACP session ID
        """
        if not self._connection:
            return

        # Quick check for obvious issues (can be expanded)
        for code_block in code_blocks:
            code = code_block.get("content", "")
            if not code:
                continue

            # Quick security check
            security_keywords = ["password", "secret", "api_key", "token", "credential"]
            if any(keyword in code.lower() for keyword in security_keywords):
                await self._connection.session_update(
                    session_id=session_id,
                    update=update_agent_message(
                        text_block("⚠️ CodeOptiX: Potential security issue detected in code")
                    ),
                    source="codeoptix",
                )

    def on_connect(self, conn: Any) -> None:
        """Called when client connects to agent."""
        logger.debug("Bridge connected to ACP agent")
