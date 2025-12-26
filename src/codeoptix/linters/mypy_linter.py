"""mypy type checker linter integration."""

import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class MypyLinter(BaseLinter):
    """mypy static type checker."""

    def __init__(self, config: dict | None = None):
        """Initialize mypy linter."""
        super().__init__(config)
        self.name = "mypy"

    def is_available(self) -> bool:
        """Check if mypy is available."""
        try:
            subprocess.run(
                ["mypy", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _find_config_file(self, path: str) -> Path | None:
        """Find mypy configuration file."""
        path_obj = Path(path)

        config_files = [
            "mypy.ini",
            ".mypy.ini",
            "setup.cfg",
            "pyproject.toml",
        ]

        current = path_obj if path_obj.is_file() else path_obj.parent
        while current != current.parent:
            for config_file in config_files:
                config_path = current / config_file
                if config_path.exists():
                    # For pyproject.toml, check if it has [tool.mypy] section
                    if config_file == "pyproject.toml":
                        try:
                            with open(config_path) as f:
                                content = f.read()
                                if "[tool.mypy]" in content:
                                    return config_path
                        except OSError:
                            pass
                    else:
                        return config_path
            current = current.parent

        return None

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run mypy on code."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["mypy not found in PATH. Install with: pip install mypy"],
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

        # Find config file (mypy automatically uses it)
        self._find_config_file(path)

        # Build command
        cmd = ["mypy", "--show-error-codes", "--no-error-summary"]

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
                errors=["mypy execution timed out"],
                execution_time=120.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"mypy error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse mypy output."""
        import re

        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        # mypy format: filename:line: error: message [error-code]
        pattern = r"(.+?):(\d+):\s*(error|note|warning):\s*(.+?)(?:\s+\[(.+?)\])?$"

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                file_path, line_num, level, message, error_code = match.groups()

                # Map mypy levels to severity
                if level == "error":
                    severity = Severity.HIGH
                elif level == "warning":
                    severity = Severity.MEDIUM
                else:
                    severity = Severity.LOW

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=message.strip(),
                    file=file_path,
                    line=int(line_num) if line_num.isdigit() else None,
                    rule_id=error_code,
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
