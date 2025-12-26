"""Linter integration for CodeOptiX - works without API keys."""

from codeoptix.linters.base import LinterIssue, LinterResult, Severity
from codeoptix.linters.language_detector import LanguageDetector
from codeoptix.linters.runner import LinterRunner

__all__ = [
    "LanguageDetector",
    "LinterIssue",
    "LinterResult",
    "LinterRunner",
    "Severity",
]
