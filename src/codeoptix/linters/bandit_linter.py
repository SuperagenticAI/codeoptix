"""Bandit security linter integration."""

import json
import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class BanditLinter(BaseLinter):
    """Bandit security linter."""

    def __init__(self, config: dict | None = None):
        """Initialize Bandit linter."""
        super().__init__(config)
        self.name = "bandit"
        self.severity_map = {
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
        }

    def is_available(self) -> bool:
        """Check if bandit is available."""
        try:
            subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run bandit on code."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["Bandit not found in PATH. Install with: pip install bandit"],
                execution_time=0.0,
            )

        path_obj = Path(path)
        if not path_obj.exists():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Path not found: {path}"],
                execution_time=0.0,
            )

        # Build command
        cmd = ["bandit", "-f", "json", "-q", "-r"]

        # Add specific files if provided
        if files:
            cmd.extend(files)
        else:
            cmd.append(str(path_obj))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            execution_time = time.time() - start_time
            return self.parse_output(
                result.stdout,
                result.stderr,
                result.returncode,
                execution_time,
            )
        except subprocess.TimeoutExpired:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["Bandit execution timed out"],
                execution_time=60.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Bandit error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse bandit JSON output."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        try:
            data = json.loads(output)

            # Bandit returns results in "results" key
            for item in data.get("results", []):
                severity = self.severity_map.get(
                    item.get("issue_severity", "LOW"),
                    Severity.LOW,
                )

                # Bandit severity mapping
                if item.get("issue_confidence", "LOW") == "HIGH" and severity == Severity.LOW:
                    severity = Severity.MEDIUM

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=item.get("issue_text", "Unknown issue"),
                    file=item.get("filename", ""),
                    line=item.get("line_number"),
                    code=item.get("code"),
                    rule_id=item.get("test_id"),
                    confidence=self._parse_confidence(item.get("issue_confidence")),
                )
                issues.append(issue)

            return LinterResult(
                linter=self.name,
                success=returncode == 0 or len(issues) == 0,
                issues=issues,
                errors=errors,
                execution_time=execution_time,
                raw_output=output,
            )
        except json.JSONDecodeError:
            errors.append("Failed to parse bandit JSON output")
            return LinterResult(
                linter=self.name,
                success=False,
                issues=issues,
                errors=errors,
                execution_time=execution_time,
                raw_output=output,
            )

    def _parse_confidence(self, confidence: str | None) -> float | None:
        """Parse confidence string to float."""
        if not confidence:
            return None

        confidence_map = {
            "HIGH": 0.9,
            "MEDIUM": 0.6,
            "LOW": 0.3,
        }
        return confidence_map.get(confidence.upper(), 0.5)
