"""Agent Orchestration - Route to best agent for each task."""

import logging
from typing import Any

from acp import text_block

from codeoptix.acp.code_extractor import extract_code_from_message, extract_code_from_text
from codeoptix.acp.registry import ACPAgentRegistry
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMClient

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple ACP agents for task execution."""

    def __init__(
        self,
        registry: ACPAgentRegistry,
        evaluation_engine: EvaluationEngine | None = None,
        llm_client: LLMClient | None = None,
    ):
        """Initialize agent orchestrator.

        Args:
            registry: ACP agent registry
            evaluation_engine: Optional evaluation engine
            llm_client: Optional LLM client
        """
        self.registry = registry
        self.evaluation_engine = evaluation_engine
        self.llm_client = llm_client

    async def route_to_agent(
        self,
        prompt: str,
        agent_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route a prompt to the best agent.

        Args:
            prompt: The prompt to execute
            agent_name: Specific agent name (if None, selects best agent)
            context: Additional context

        Returns:
            Result dictionary with agent response and metadata
        """
        # Select agent
        if agent_name:
            selected_agent = agent_name
        else:
            selected_agent = await self._select_best_agent(prompt, context)

        if not selected_agent:
            raise ValueError("No agent available")

        # Connect to agent
        connection = await self.registry.connect(selected_agent)
        session_id = self.registry.get_session_id(selected_agent)

        if not session_id:
            raise RuntimeError(f"No session ID for agent {selected_agent}")

        # Send prompt
        response = await connection.prompt(
            session_id=session_id,
            prompt=[text_block(prompt)],
        )

        return {
            "agent": selected_agent,
            "response": response,
            "session_id": session_id,
        }

    async def _select_best_agent(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """Select the best agent for a given prompt.

        Args:
            prompt: The prompt
            context: Additional context

        Returns:
            Agent name or None if no agents available
        """
        agents = self.registry.list_agents()
        if not agents:
            return None

        # Intelligent agent selection based on:
        # - Agent capabilities (from registry)
        # - Task type (inferred from prompt)
        # - Context requirements

        # Check if context specifies an agent
        if context and "preferred_agent" in context:
            preferred = context["preferred_agent"]
            if preferred in agents:
                return preferred

        # Infer task type from prompt
        prompt_lower = prompt.lower()

        # Security-focused tasks
        if any(
            keyword in prompt_lower
            for keyword in ["security", "secure", "vulnerability", "exploit", "attack"]
        ):
            # Prefer agents with security capabilities
            for agent_name in agents:
                agent_config = self.registry.get_agent(agent_name)
                if agent_config and "security" in [c.lower() for c in agent_config.capabilities]:
                    return agent_name

        # Code review tasks
        if any(keyword in prompt_lower for keyword in ["review", "critique", "judge", "evaluate"]):
            # Prefer agents with review capabilities
            for agent_name in agents:
                agent_config = self.registry.get_agent(agent_name)
                if agent_config and "review" in [c.lower() for c in agent_config.capabilities]:
                    return agent_name

        # Default: use first available agent
        return agents[0]

    async def execute_multi_agent_workflow(
        self,
        workflow: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Execute a multi-agent workflow.

        Args:
            workflow: List of workflow steps, each with 'agent', 'prompt', etc.

        Returns:
            List of results from each step
        """
        results = []
        for step in workflow:
            agent_name = step.get("agent")
            prompt = step.get("prompt", "")
            context = step.get("context", {})

            result = await self.route_to_agent(
                prompt=prompt,
                agent_name=agent_name,
                context=context,
            )
            results.append(result)

        return results


class MultiAgentJudge:
    """Multi-agent judge - Use different agents for generation vs. judgment."""

    def __init__(
        self,
        registry: ACPAgentRegistry,
        generate_agent: str,
        judge_agent: str,
        evaluation_engine: EvaluationEngine | None = None,
        llm_client: LLMClient | None = None,
    ):
        """Initialize multi-agent judge.

        Args:
            registry: ACP agent registry
            generate_agent: Name of agent for code generation
            judge_agent: Name of agent for code judgment/critique
            evaluation_engine: Optional evaluation engine
            llm_client: Optional LLM client
        """
        self.registry = registry
        self.generate_agent = generate_agent
        self.judge_agent = judge_agent
        self.evaluation_engine = evaluation_engine
        self.llm_client = llm_client

    async def generate_and_judge(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate code with one agent and judge with another.

        Args:
            prompt: The prompt for code generation
            context: Additional context

        Returns:
            Dictionary with generated code, judgment, and evaluation results
        """
        # Step 1: Generate code with generate agent
        generate_conn = await self.registry.connect(self.generate_agent)
        generate_session = self.registry.get_session_id(self.generate_agent)

        if not generate_session:
            raise RuntimeError(f"No session for generate agent {self.generate_agent}")

        generate_response = await generate_conn.prompt(
            session_id=generate_session,
            prompt=[text_block(prompt)],
        )

        # Extract generated code (simplified - would need proper extraction)
        generated_code = self._extract_code_from_response(generate_response)

        # Step 2: Judge code with judge agent
        judge_prompt = f"""Please review and critique the following code:

```python
{generated_code}
```

Provide a detailed critique focusing on:
- Code quality and best practices
- Potential bugs or issues
- Security concerns
- Performance considerations
- Suggestions for improvement
"""

        judge_conn = await self.registry.connect(self.judge_agent)
        judge_session = self.registry.get_session_id(self.judge_agent)

        if not judge_session:
            raise RuntimeError(f"No session for judge agent {self.judge_agent}")

        judge_response = await judge_conn.prompt(
            session_id=judge_session,
            prompt=[text_block(judge_prompt)],
        )

        # Extract judgment
        judgment = self._extract_text_from_response(judge_response)

        # Step 3: Evaluate both with CodeOptiX
        evaluation_results = None
        if self.evaluation_engine:
            from codeoptix.adapters.base import AgentOutput

            AgentOutput(
                code=generated_code,
                tests="",
                messages=[],
                metadata={"source": "multi_agent_judge", "judgment": judgment},
            )

            # Evaluate behaviors
            evaluation_results = await self.evaluation_engine.evaluate_behaviors(
                behavior_names=["insecure-code", "vacuous-tests", "plan-drift"],
                context={"code": generated_code, "judgment": judgment},
            )

        return {
            "generated_code": generated_code,
            "judgment": judgment,
            "evaluation_results": evaluation_results,
            "generate_agent": self.generate_agent,
            "judge_agent": self.judge_agent,
        }

    def _extract_code_from_response(self, response: Any) -> str:
        """Extract code from agent response.

        Args:
            response: ACP prompt response

        Returns:
            Extracted code as string
        """
        if not response:
            return ""

        # Extract from response messages
        code_blocks = []

        # Check if response has messages
        if hasattr(response, "messages"):
            for message in response.messages:
                if hasattr(message, "content"):
                    content = message.content
                    if isinstance(content, str):
                        code_blocks.extend(extract_code_from_text(content))
                    elif hasattr(content, "text"):
                        code_blocks.extend(extract_code_from_text(getattr(content, "text", "")))

        # Check if response has updates
        if hasattr(response, "updates"):
            for update in response.updates:
                code_blocks.extend(extract_code_from_message(update))

        # Combine all code blocks
        if code_blocks:
            # Prefer code blocks over inline code
            block_codes = [cb["content"] for cb in code_blocks if cb.get("type") == "block"]
            if block_codes:
                return "\n\n".join(block_codes)
            # Fallback to inline code
            inline_codes = [cb["content"] for cb in code_blocks if cb.get("type") == "inline"]
            if inline_codes:
                return "\n".join(inline_codes)

        return ""

    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text from agent response.

        Args:
            response: ACP prompt response

        Returns:
            Extracted text as string
        """
        if not response:
            return ""

        text_parts = []

        # Check if response has messages
        if hasattr(response, "messages"):
            for message in response.messages:
                if hasattr(message, "content"):
                    content = message.content
                    if isinstance(content, str):
                        text_parts.append(content)
                    elif hasattr(content, "text"):
                        text_parts.append(getattr(content, "text", ""))

        # Check if response has updates
        if hasattr(response, "updates"):
            for update in response.updates:
                if hasattr(update, "content"):
                    content = update.content
                    if isinstance(content, str):
                        text_parts.append(content)
                    elif hasattr(content, "text"):
                        text_parts.append(getattr(content, "text", ""))

        return "\n".join(text_parts)
