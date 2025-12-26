"""ACP (Agent Client Protocol) integration for CodeOptiX.

This module provides ACP integration:
- CodeOptiX as an ACP agent (can be used by editors)
- ACP client adapter (connect to other agents via ACP)
- Quality bridge functionality
- Agent registry and orchestration
- Multi-agent judge support
"""

from codeoptix.acp.agent import CodeOptiXAgent
from codeoptix.acp.bridge import ACPQualityBridge
from codeoptix.acp.client_adapter import ACPClientAdapter
from codeoptix.acp.code_extractor import (
    extract_all_code,
    extract_code_from_message,
    extract_code_from_text,
)
from codeoptix.acp.orchestrator import AgentOrchestrator, MultiAgentJudge
from codeoptix.acp.registry import ACPAgentConfig, ACPAgentRegistry

__all__ = [
    "ACPAgentConfig",
    "ACPAgentRegistry",
    "ACPClientAdapter",
    "ACPQualityBridge",
    "AgentOrchestrator",
    "CodeOptiXAgent",
    "MultiAgentJudge",
    "extract_all_code",
    "extract_code_from_message",
    "extract_code_from_text",
]
