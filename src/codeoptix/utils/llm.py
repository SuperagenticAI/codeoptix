"""LLM client abstraction for multiple providers."""

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import anthropic
import openai
from google import genai


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion."""

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider."""


class AnthropicClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, api_key: str | None = None):
        """Initialize Anthropic client."""
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "claude-opus-4-5-20251101",
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion using Anthropic."""
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_message = content
            elif role == "user":
                anthropic_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                anthropic_messages.append({"role": "assistant", "content": content})

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens or 4096,
            temperature=temperature,
            system=system_message,
            messages=anthropic_messages,
            **kwargs,
        )

        # Extract text content from response
        if response.content and len(response.content) > 0:
            if hasattr(response.content[0], "text"):
                return response.content[0].text
            return str(response.content[0])
        return ""

    def get_available_models(self) -> list[str]:
        """Get available Anthropic models."""
        return [
            "claude-opus-4-5-20251101",
            "claude-sonnet-4-5-20251101",
            "claude-haiku-4-5-20251101",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]


class OpenAIClient(LLMClient):
    """OpenAI GPT client."""

    def __init__(self, api_key: str | None = None):
        """Initialize OpenAI client."""
        self.client = openai.OpenAI(api_key=api_key)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-5.2",
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion using OpenAI."""
        response = self.client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""
        return ""

    def get_available_models(self) -> list[str]:
        """Get available OpenAI models."""
        return [
            "gpt-5.2",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
        ]


class GoogleClient(LLMClient):
    """Google Gemini client using google-genai SDK."""

    def __init__(self, api_key: str | None = None):
        """Initialize Google client."""
        # Use the new google-genai Client API
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion using Google Gemini."""
        # Convert messages to the new API format
        # The new API uses Contents format with role and parts
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            else:
                # Create Content object with role and parts
                contents.append({"role": role, "parts": [{"text": content}]})

        # Build the config
        config_dict = {
            "temperature": temperature,
        }
        if max_tokens:
            config_dict["max_output_tokens"] = max_tokens
        if system_instruction:
            config_dict["system_instruction"] = {"parts": [{"text": system_instruction}]}

        # Generate content using the new API
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config_dict,
        )

        # Extract text from response
        # The new API returns response with text attribute or candidates
        if hasattr(response, "text") and response.text:
            return response.text
        if hasattr(response, "candidates") and response.candidates:
            # Handle structured response with candidates
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)
                if text_parts:
                    return "".join(text_parts)
        # Fallback to string representation
        return str(response)

    def get_available_models(self) -> list[str]:
        """Get available Google models."""
        return [
            "gemini-3-pro",
            "gemini-3-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-pro",
        ]


class OllamaClient(LLMClient):
    """Ollama local model client (http://localhost:11434)."""

    def __init__(self, api_key: str | None = None, model: str = "llama3.1", **kwargs: Any):
        """Initialize Ollama client.

        api_key is unused but kept for interface compatibility.
        """
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # Normalize: strip trailing slash
        self.base_url = base.rstrip("/")
        # Verify connection on init (best-effort, don't fail if it's down)
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify Ollama connection (best-effort, non-blocking)."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"Content-Type": "application/json"},
                method="GET",
            )
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            # Connection failed, but don't raise - let the actual call handle it
            # This is just a warning check
            pass

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "llama3.1",
        temperature: float = 1.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion using a local Ollama model."""
        # Use Ollama's chat API which properly handles chat messages
        payload = {
            "model": model,
            "messages": messages,  # Pass messages directly
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            # Increase timeout for large models like gpt-oss:120b which can take longer
            with urllib.request.urlopen(req, timeout=300) as resp:  # 5 minutes for large models
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as exc:  # pragma: no cover - network/env specific
            # Provide helpful error message
            default_url = "http://localhost:11434"
            if self.base_url != default_url:
                hint = f" (OLLAMA_BASE_URL is set to {self.base_url}, default is {default_url})"
            else:
                hint = " (default port is 11434)"
            raise RuntimeError(
                f"Failed to contact Ollama at {self.base_url}. "
                f"Is the Ollama daemon running?{hint}\n"
                f"  Try: ollama serve\n"
                f"  Or set OLLAMA_BASE_URL to the correct URL if using a custom port."
            ) from exc

        try:
            obj = json.loads(body)
        except json.JSONDecodeError as exc:  # pragma: no cover - unexpected response
            raise RuntimeError(f"Invalid JSON from Ollama: {body!r}") from exc

        # Ollama chat API: response["message"]["content"]
        # Fallback to generate API format for backward compatibility
        if "message" in obj and "content" in obj["message"]:
            return obj["message"]["content"]
        return obj.get("response", "")

    def get_available_models(self) -> list[str]:
        """Get available Ollama models via /api/tags."""
        req = urllib.request.Request(
            f"{self.base_url}/api/tags",
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
            obj = json.loads(body)
        except Exception:  # pragma: no cover - best-effort helper
            return []

        models = []
        for m in obj.get("models", []) or []:
            name = m.get("name")
            if isinstance(name, str):
                models.append(name)
        return models


def create_llm_client(
    provider: LLMProvider, api_key: str | None = None, model: str | None = None
) -> LLMClient:
    """Factory function to create an LLM client."""
    if provider == LLMProvider.ANTHROPIC:
        return AnthropicClient(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
    if provider == LLMProvider.OPENAI:
        return OpenAIClient(api_key=api_key, model=model or "gpt-4o")
    if provider == LLMProvider.GOOGLE:
        return GoogleClient(api_key=api_key, model=model or "gemini-1.5-pro")
    if provider == LLMProvider.OLLAMA:
        return OllamaClient(model=model or "llama3.1")
    raise ValueError(f"Unsupported provider: {provider}")
