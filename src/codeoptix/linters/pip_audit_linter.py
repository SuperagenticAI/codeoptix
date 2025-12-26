"""pip-audit package vulnerability linter integration."""

import json
import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class PipAuditLinter(BaseLinter):
    """pip-audit package vulnerability scanner."""

    def __init__(self, config: dict | None = None):
        """Initialize pip-audit linter."""
        super().__init__(config)
        self.name = "pip-audit"

    def is_available(self) -> bool:
        """Check if pip-audit is available."""
        try:
            subprocess.run(
                ["pip-audit", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run pip-audit on packages."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["pip-audit not found in PATH. Install with: pip install pip-audit"],
                execution_time=0.0,
            )

        try:
            # Build command
            cmd = ["pip-audit", "--format=json"]

            # Check for requirements file
            path_obj = Path(path)
            if path_obj.is_file() and path_obj.name in ["requirements.txt", "requirements-dev.txt"]:
                cmd.extend(["--requirement", str(path_obj)])
            elif path_obj.is_dir():
                req_file = path_obj / "requirements.txt"
                if req_file.exists():
                    cmd.extend(["--requirement", str(req_file)])

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
                errors=["pip-audit execution timed out"],
                execution_time=60.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"pip-audit error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse pip-audit JSON output."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        try:
            data = json.loads(output) if output.strip() else {}

            # pip-audit JSON format: {"vulnerabilities": [...]}
            vulnerabilities = data.get("vulnerabilities", [])

            for vuln in vulnerabilities:
                name = vuln.get("name", "unknown")
                installed_version = vuln.get("installed_version", "")
                vuln_id = vuln.get("id", "")
                fix_versions = vuln.get("fix_versions", [])

                # Determine severity
                severity = Severity.HIGH
                if "critical" in str(vuln).lower():
                    severity = Severity.CRITICAL

                message = f"{name} {installed_version}: {vuln_id}"
                if fix_versions:
                    message += f" [Fix: {', '.join(fix_versions)}]"

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=message,
                    file="requirements.txt",
                    rule_id=vuln_id,
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
            errors.append("Failed to parse pip-audit JSON output")
            return LinterResult(
                linter=self.name,
                success=False,
                issues=issues,
                errors=errors,
                execution_time=execution_time,
                raw_output=output,
            )
