"""Pylint code quality linter integration."""

import json
import re
import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class PylintLinter(BaseLinter):
    """Pylint code quality linter."""

    def __init__(self, config: dict | None = None):
        """Initialize Pylint linter."""
        super().__init__(config)
        self.name = "pylint"
        self.severity_map = {
            "E": Severity.HIGH,  # Error
            "W": Severity.MEDIUM,  # Warning
            "C": Severity.LOW,  # Convention
            "R": Severity.LOW,  # Refactor
            "F": Severity.CRITICAL,  # Fatal
        }

    def is_available(self) -> bool:
        """Check if pylint is available."""
        try:
            subprocess.run(
                ["pylint", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run pylint on code."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["Pylint not found in PATH. Install with: pip install pylint"],
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
        cmd = [
            "pylint",
            "--output-format=json",
            "--disable=all",
            "--enable=E,F,W,C,R",  # Enable all message types
        ]

        # Add specific files if provided
        if files:
            cmd.extend(files)
        # Find Python files
        elif (path_obj.is_file() and path_obj.suffix == ".py") or path_obj.is_dir():
            cmd.append(str(path_obj))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
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
                errors=["Pylint execution timed out"],
                execution_time=120.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Pylint error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse pylint JSON output."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        try:
            data = json.loads(output)

            for item in data:
                message_type = item.get("type", "W")
                severity = self.severity_map.get(message_type, Severity.MEDIUM)

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=item.get("message", "Unknown issue"),
                    file=item.get("path", ""),
                    line=item.get("line"),
                    column=item.get("column"),
                    code=item.get("symbol"),
                    rule_id=item.get("message-id"),
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
            # Try parsing text output as fallback
            return self._parse_text_output(output, stderr, returncode, execution_time)

    def _parse_text_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse pylint text output as fallback."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        # Pylint text format: filename:line:column: message-type: message (message-id)
        pattern = r"(.+?):(\d+):(\d+):\s*([EWCRF]):\s*(.+?)\s*\((.+?)\)"

        for line in output.split("\n"):
            match = re.match(pattern, line)
            if match:
                file_path, line_num, col_num, msg_type, message, rule_id = match.groups()
                severity = self.severity_map.get(msg_type, Severity.MEDIUM)

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=message.strip(),
                    file=file_path,
                    line=int(line_num) if line_num.isdigit() else None,
                    column=int(col_num) if col_num.isdigit() else None,
                    rule_id=rule_id,
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
