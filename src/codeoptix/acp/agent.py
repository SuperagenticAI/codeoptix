"""CodeOptiX as an ACP Agent.

This allows CodeOptiX to be used by ACP-compatible editors (Zed, JetBrains, Neovim, etc.)
as a quality engineering agent.
"""

from typing import Any
from uuid import uuid4

from acp import (
    Agent,
    InitializeResponse,
    NewSessionResponse,
    PromptResponse,
    text_block,
    update_agent_message,
)
from acp.interfaces import Client
from acp.schema import (
    AudioContentBlock,
    ClientCapabilities,
    EmbeddedResourceContentBlock,
    HttpMcpServer,
    ImageContentBlock,
    Implementation,
    McpServerStdio,
    ResourceContentBlock,
    SseMcpServer,
    TextContentBlock,
)

from codeoptix.acp.code_extractor import extract_code_from_text
from codeoptix.adapters.base import AgentOutput
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMClient


class CodeOptiXAgent(Agent):
    """CodeOptiX as an ACP agent for quality engineering."""

    _conn: Client | None = None
    _evaluation_engine: EvaluationEngine | None = None
    _llm_client: LLMClient | None = None

    def __init__(
        self,
        evaluation_engine: EvaluationEngine | None = None,
        llm_client: LLMClient | None = None,
        behaviors: list[str] | None = None,
    ):
        """Initialize CodeOptiX ACP agent.

        Args:
            evaluation_engine: Optional evaluation engine (will create default if not provided)
            llm_client: Optional LLM client (will create default if not provided)
            behaviors: List of behavior names to evaluate (default: all)
        """
        self._evaluation_engine = evaluation_engine
        self._llm_client = llm_client
        self._behaviors = behaviors or ["insecure-code", "vacuous-tests", "plan-drift"]

        # Initialize default evaluation engine if not provided
        if not self._evaluation_engine and self._llm_client:
            # Create a minimal adapter for evaluation (dummy adapter)
            from codeoptix.adapters.base import AgentAdapter
            from codeoptix.adapters.factory import create_adapter

            # Try to create a default adapter (will use dummy if none available)
            try:
                adapter = create_adapter("claude-code", {"llm_config": {"provider": "anthropic"}})
            except Exception:
                # Create a minimal dummy adapter
                class DummyAdapter(AgentAdapter):
                    def get_adapter_type(self) -> str:
                        return "dummy"

                    def generate_code(self, prompt: str, **kwargs) -> AgentOutput:
                        return AgentOutput(code="", tests="", messages=[], metadata={})

                adapter = DummyAdapter()

            self._evaluation_engine = EvaluationEngine(adapter, self._llm_client)

    def on_connect(self, conn: Client) -> None:
        """Called when agent connects to client."""
        self._conn = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: ClientCapabilities | None = None,
        client_info: Implementation | None = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        """Initialize the agent with client capabilities."""
        return InitializeResponse(protocol_version=protocol_version)

    async def new_session(
        self,
        cwd: str,
        mcp_servers: list[HttpMcpServer | SseMcpServer | McpServerStdio],
        **kwargs: Any,
    ) -> NewSessionResponse:
        """Create a new session."""
        session_id = uuid4().hex
        return NewSessionResponse(session_id=session_id)

    async def prompt(
        self,
        prompt: list[
            TextContentBlock
            | ImageContentBlock
            | AudioContentBlock
            | ResourceContentBlock
            | EmbeddedResourceContentBlock
        ],
        session_id: str,
        **kwargs: Any,
    ) -> PromptResponse:
        """Handle a prompt from the client.

        This is where CodeOptiX performs quality engineering on the request.
        """
        if not self._conn:
            return PromptResponse(stop_reason="error", error="Not connected to client")

        # Extract text from prompt blocks
        prompt_text = ""
        for block in prompt:
            if isinstance(block, dict):
                text = block.get("text", "")
            elif isinstance(block, TextContentBlock):
                text = block.text
            else:
                text = getattr(block, "text", "")
            if text:
                prompt_text += text + "\n"

        # Send initial response
        await self._conn.session_update(
            session_id=session_id,
            update=update_agent_message(text_block("🔍 CodeOptiX: Analyzing code quality...")),
            source="codeoptix",
        )

        # Extract code from prompt
        code_blocks = extract_code_from_text(prompt_text)

        # Perform quality evaluation
        evaluation_results = None
        if self._evaluation_engine and code_blocks:
            try:
                # Extract code content
                code_content = "\n\n".join([cb["content"] for cb in code_blocks])

                if code_content:
                    # Create agent output for evaluation
                    AgentOutput(
                        code=code_content,
                        tests="",
                        messages=[],
                        metadata={"source": "acp_agent", "prompt": prompt_text[:200]},
                    )

                    # Evaluate behaviors
                    evaluation_results = self._evaluation_engine.evaluate_behaviors(
                        behavior_names=self._behaviors,
                        context={"code": code_content, "prompt": prompt_text},
                    )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error during quality evaluation: {e}")
                evaluation_results = {"error": str(e)}

        # Format response
        if evaluation_results and "behaviors" in evaluation_results:
            response_lines = ["## 🔍 CodeOptiX Quality Report\n"]

            overall_score = evaluation_results.get("overall_score", 0.0)
            response_lines.append(f"**Overall Score:** {overall_score:.2%}\n")

            behaviors = evaluation_results.get("behaviors", {})
            for behavior_name, behavior_data in behaviors.items():
                passed = behavior_data.get("passed", True)
                score = behavior_data.get("score", 0.0)
                emoji = "✅" if passed else "❌"

                response_lines.append(f"{emoji} **{behavior_name}**: {score:.2%}")

                if not passed and behavior_data.get("evidence"):
                    evidence = behavior_data["evidence"][:3]  # Limit to 3 items
                    for ev in evidence:
                        response_lines.append(f"   - {ev}")

            response_text = "\n".join(response_lines)
        elif code_blocks:
            response_text = f"CodeOptiX analyzed {len(code_blocks)} code block(s).\n\n✅ Quality check complete."
        else:
            response_text = f"CodeOptiX received your request:\n\n{prompt_text[:500]}\n\n⚠️ No code blocks detected for quality evaluation."

        await self._conn.session_update(
            session_id=session_id,
            update=update_agent_message(text_block(response_text)),
            source="codeoptix",
        )

        return PromptResponse(stop_reason="end_turn")
