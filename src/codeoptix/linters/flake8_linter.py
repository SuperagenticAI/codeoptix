"""Flake8 style guide linter integration."""

import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class Flake8Linter(BaseLinter):
    """Flake8 style guide linter."""

    def __init__(self, config: dict | None = None):
        """Initialize Flake8 linter."""
        super().__init__(config)
        self.name = "flake8"
        self.severity_map = {
            "E": Severity.HIGH,  # Error
            "W": Severity.MEDIUM,  # Warning
            "F": Severity.HIGH,  # Pyflakes
            "C": Severity.LOW,  # McCabe complexity
            "N": Severity.LOW,  # Naming
            "B": Severity.MEDIUM,  # flake8-bugbear
        }

    def is_available(self) -> bool:
        """Check if flake8 is available."""
        try:
            subprocess.run(
                ["flake8", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run flake8 on code."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["Flake8 not found in PATH. Install with: pip install flake8"],
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
        cmd = ["flake8"]

        # Add specific files if provided
        if files:
            cmd.extend(files)
        elif path_obj.is_file() or path_obj.is_dir():
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
                errors=["Flake8 execution timed out"],
                execution_time=60.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Flake8 error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse flake8 output."""
        import re

        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        # Flake8 format: filename:line:column: code message
        pattern = r"(.+?):(\d+):(\d+):\s*([EWFNCB]\d+)\s+(.+?)$"

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                file_path, line_num, col_num, code, message = match.groups()

                # Determine severity from error code
                error_type = code[0] if code else "W"
                severity = self.severity_map.get(error_type, Severity.MEDIUM)

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=message.strip(),
                    file=file_path,
                    line=int(line_num) if line_num.isdigit() else None,
                    column=int(col_num) if col_num.isdigit() else None,
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
