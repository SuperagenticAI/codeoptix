"""Linter runner that orchestrates multiple linters."""

import time
from typing import Any

from codeoptix.linters.bandit_linter import BanditLinter
from codeoptix.linters.base import BaseLinter
from codeoptix.linters.coverage_linter import CoverageLinter
from codeoptix.linters.flake8_linter import Flake8Linter
from codeoptix.linters.html_accessibility_linter import HTMLAccessibilityLinter
from codeoptix.linters.language_detector import LanguageDetector
from codeoptix.linters.mypy_linter import MypyLinter
from codeoptix.linters.pip_audit_linter import PipAuditLinter
from codeoptix.linters.pylint_linter import PylintLinter
from codeoptix.linters.ruff_linter import RuffLinter
from codeoptix.linters.safety_linter import SafetyLinter


class LinterRunner:
    """Runs multiple linters and aggregates results."""

    # Registry of available linters (zero new dependencies)
    LINTER_REGISTRY = {
        # Code Quality (fastest first)
        "ruff": RuffLinter,  # Fastest - should be first
        "pylint": PylintLinter,
        "flake8": Flake8Linter,
        "mypy": MypyLinter,  # Type checking
        # Security
        "bandit": BanditLinter,
        "safety": SafetyLinter,  # Dependency vulnerabilities
        "pip-audit": PipAuditLinter,  # Package audit
        # Testing
        "coverage": CoverageLinter,  # Test coverage
        # Accessibility (custom, no dependency)
        "html-accessibility": HTMLAccessibilityLinter,  # Custom HTML analyzer
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize linter runner."""
        self.config = config or {}
        self.linters: dict[str, BaseLinter] = {}

        # Initialize enabled linters
        # Default: Use all available linters (zero new dependencies)
        enabled_linters = self.config.get("linters", list(self.LINTER_REGISTRY.keys()))
        for linter_name in enabled_linters:
            if linter_name in self.LINTER_REGISTRY:
                linter_config = self.config.get("linter_config", {}).get(linter_name, {})
                try:
                    self.linters[linter_name] = self.LINTER_REGISTRY[linter_name](linter_config)
                except Exception:
                    # Skip linters that fail to initialize
                    pass

    def run_linters(
        self,
        path: str,
        linter_names: list[str] | None = None,
        files: list[str] | None = None,
        auto_detect: bool = True,
    ) -> dict[str, Any]:
        """
        Run specified linters on code.

        Args:
            path: Path to code (file or directory)
            linter_names: List of linter names to run (None = auto-detect or all enabled)
            files: Optional list of specific files to check
            auto_detect: Auto-detect language and select appropriate linters

        Returns:
            Dictionary with aggregated results
        """
        start_time = time.time()

        # Auto-detect language and linters if requested
        if linter_names is None and auto_detect:
            if files:
                # Detect from file list
                detected_linters = LanguageDetector.get_linters_for_files(files)
                # Find existing configs
                config_files = LanguageDetector.find_config_files(path)
                # Prioritize linters with existing configs
                linter_names = []
                for linter in detected_linters:
                    if linter in config_files or linter in self.LINTER_REGISTRY:
                        linter_names.append(linter)
                # If no detected linters, use all available
                if not linter_names:
                    linter_names = list(self.linters.keys())
            else:
                # Use all enabled linters
                linter_names = list(self.linters.keys())
        elif linter_names is None:
            linter_names = list(self.linters.keys())

        # Filter to available linters
        available_linters = {
            name: linter
            for name, linter in self.linters.items()
            if name in linter_names and linter.is_available()
        }

        if not available_linters:
            return {
                "success": False,
                "errors": [
                    "No linters available. Install linters: pip install bandit pylint flake8"
                ],
                "results": {},
                "summary": {
                    "total_issues": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                },
                "execution_time": time.time() - start_time,
            }

        # Run each linter
        results = {}
        all_issues = []
        all_errors = []

        for linter_name, linter in available_linters.items():
            try:
                result = linter.run(path, files=files)
                results[linter_name] = result.to_dict()
                all_issues.extend(result.issues)
                all_errors.extend(result.errors)
            except Exception as e:
                all_errors.append(f"{linter_name} error: {e!s}")
                results[linter_name] = {
                    "success": False,
                    "issues": [],
                    "errors": [str(e)],
                }

        # Aggregate summary
        summary = self._aggregate_summary(all_issues)

        execution_time = time.time() - start_time

        return {
            "success": len(all_issues) == 0 and len(all_errors) == 0,
            "results": results,
            "summary": summary,
            "issues": [issue.to_dict() for issue in all_issues],
            "errors": all_errors,
            "execution_time": execution_time,
        }

    def _aggregate_summary(self, issues: list) -> dict[str, int]:
        """Aggregate issue summary by severity."""
        summary = {
            "total_issues": len(issues),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for issue in issues:
            severity = (
                issue.severity if hasattr(issue, "severity") else issue.get("severity", "low")
            )
            if isinstance(severity, str):
                severity_key = severity.lower()
            else:
                severity_key = severity.value.lower()

            if severity_key in summary:
                summary[severity_key] += 1

        return summary

    def get_available_linters(self) -> list[str]:
        """Get list of available linters."""
        return [name for name, linter in self.linters.items() if linter.is_available()]

    def get_all_linters(self) -> list[str]:
        """Get list of all registered linters."""
        return list(self.LINTER_REGISTRY.keys())
