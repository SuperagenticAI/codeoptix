"""Ruff linter integration - extremely fast Python linter."""

import json
import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class RuffLinter(BaseLinter):
    """Ruff linter - extremely fast Python linter written in Rust."""

    def __init__(self, config: dict | None = None):
        """Initialize Ruff linter."""
        super().__init__(config)
        self.name = "ruff"
        self.severity_map = {
            "E": Severity.HIGH,  # Error
            "W": Severity.MEDIUM,  # Warning
            "F": Severity.HIGH,  # Pyflakes
            "I": Severity.LOW,  # isort
            "N": Severity.LOW,  # pep8-naming
            "UP": Severity.LOW,  # pyupgrade
            "B": Severity.MEDIUM,  # flake8-bugbear
            "C4": Severity.LOW,  # flake8-comprehensions
            "SIM": Severity.LOW,  # flake8-simplify
        }

    def is_available(self) -> bool:
        """Check if ruff is available."""
        try:
            subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _find_config_file(self, path: str) -> Path | None:
        """Find ruff configuration file (ruff.toml, pyproject.toml, .ruff.toml)."""
        path_obj = Path(path)

        # Check common config locations
        config_files = [
            "ruff.toml",
            ".ruff.toml",
            "pyproject.toml",
        ]

        # Start from path and walk up
        current = path_obj if path_obj.is_file() else path_obj.parent
        while current != current.parent:
            for config_file in config_files:
                config_path = current / config_file
                if config_path.exists():
                    return config_path
            current = current.parent

        return None

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run ruff on code."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[
                    "Ruff not found in PATH. Install with: pip install ruff or uv tool install ruff"
                ],
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

        # Find config file (use existing project config)
        config_file = self._find_config_file(path)

        # Build command
        cmd = ["ruff", "check", "--output-format=json"]

        # Use existing config if found
        if config_file:
            # Ruff automatically uses pyproject.toml or ruff.toml in project root
            pass

        # Add specific files if provided
        if files:
            cmd.extend(files)
        elif (path_obj.is_file() and path_obj.suffix == ".py") or path_obj.is_dir():
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
                errors=["Ruff execution timed out"],
                execution_time=60.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Ruff error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse ruff JSON output."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        try:
            # Ruff JSON output is a list of diagnostic objects
            data = json.loads(output) if output.strip() else []

            for item in data:
                code = item.get("code", "")
                severity_str = item.get("severity", "warning")

                # Map ruff severity to our severity
                if severity_str == "error":
                    severity = Severity.HIGH
                elif severity_str == "warning":
                    severity = Severity.MEDIUM
                else:
                    severity = Severity.LOW

                # Determine severity from code prefix if available
                if code:
                    code_prefix = code.split(".")[0] if "." in code else code
                    if code_prefix in self.severity_map:
                        severity = self.severity_map[code_prefix]

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=item.get("message", "Unknown issue"),
                    file=item.get("filename", ""),
                    line=item.get("location", {}).get("row"),
                    column=item.get("location", {}).get("column"),
                    code=code,
                    rule_id=code,
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
            errors.append("Failed to parse ruff JSON output")
            return LinterResult(
                linter=self.name,
                success=False,
                issues=issues,
                errors=errors,
                execution_time=execution_time,
                raw_output=output,
            )
