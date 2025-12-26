"""Code extraction from ACP messages and tool calls."""

import re
from typing import Any

from acp.schema import (
    AgentMessageChunk,
    FileEditToolCallContent,
    TextContentBlock,
    ToolCallProgress,
    ToolCallStart,
)

# Patterns for extracting code from text
CODE_BLOCK_PATTERN = re.compile(
    r"```(?:python|py|javascript|js|typescript|ts|java|go|rust|cpp|c\+\+|c|ruby|php|swift|kotlin|scala|r|sql|html|css|xml|yaml|yml|json|bash|sh|shell|zsh|fish)?\n(.*?)```",
    re.DOTALL,
)
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")


def extract_code_from_text(text: str) -> list[dict[str, str]]:
    """Extract code blocks from text.

    Args:
        text: Text content to extract code from

    Returns:
        List of code blocks with language and content
    """
    code_blocks = []

    # Extract fenced code blocks
    for match in CODE_BLOCK_PATTERN.finditer(text):
        language = match.group(1) or "text"
        code = match.group(2).strip()
        if code:
            code_blocks.append({"language": language, "content": code, "type": "block"})

    # Extract inline code (less reliable, but useful)
    for match in INLINE_CODE_PATTERN.finditer(text):
        code = match.group(1).strip()
        if len(code) > 10:  # Only consider longer inline code
            code_blocks.append({"language": "text", "content": code, "type": "inline"})

    return code_blocks


def extract_code_from_message(update: Any) -> list[dict[str, str]]:
    """Extract code from an ACP message update.

    Args:
        update: ACP session update (AgentMessageChunk, ToolCallStart, etc.)

    Returns:
        List of code blocks extracted from the message
    """
    code_blocks = []

    if isinstance(update, AgentMessageChunk):
        content = update.content
        if isinstance(content, TextContentBlock):
            # Extract code from text content
            code_blocks.extend(extract_code_from_text(content.text))
        elif hasattr(content, "text"):
            # Fallback for other content types with text
            code_blocks.extend(extract_code_from_text(getattr(content, "text", "")))

    elif isinstance(update, ToolCallStart):
        tool_call = update.tool_call
        if tool_call.kind == "file_edit":
            content = tool_call.content
            if isinstance(content, FileEditToolCallContent):
                # Extract code from file edits
                if hasattr(content, "old_text") and content.old_text:
                    code_blocks.append(
                        {
                            "language": "text",
                            "content": content.old_text,
                            "type": "file_edit_old",
                            "path": getattr(content, "path", ""),
                        }
                    )
                if hasattr(content, "new_text") and content.new_text:
                    code_blocks.append(
                        {
                            "language": "text",
                            "content": content.new_text,
                            "type": "file_edit_new",
                            "path": getattr(content, "path", ""),
                        }
                    )

    elif isinstance(update, ToolCallProgress):
        tool_call = update.tool_call
        if tool_call.kind == "file_edit":
            content = tool_call.content
            if isinstance(content, FileEditToolCallContent):
                # Extract code from file edit progress
                if hasattr(content, "new_text") and content.new_text:
                    code_blocks.append(
                        {
                            "language": "text",
                            "content": content.new_text,
                            "type": "file_edit_progress",
                            "path": getattr(content, "path", ""),
                        }
                    )

    return code_blocks


def extract_all_code(updates: list[Any]) -> list[dict[str, str]]:
    """Extract all code from a list of ACP updates.

    Args:
        updates: List of ACP session updates

    Returns:
        List of all code blocks found
    """
    all_code = []
    for update in updates:
        all_code.extend(extract_code_from_message(update))
    return all_code
