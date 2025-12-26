"""Safety dependency vulnerability linter integration."""

import json
import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class SafetyLinter(BaseLinter):
    """Safety dependency vulnerability scanner."""

    def __init__(self, config: dict | None = None):
        """Initialize Safety linter."""
        super().__init__(config)
        self.name = "safety"

    def is_available(self) -> bool:
        """Check if safety is available."""
        try:
            subprocess.run(
                ["safety", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run safety on dependencies."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["Safety not found in PATH. Install with: pip install safety"],
                execution_time=0.0,
            )

        # Safety checks requirements files or installed packages
        # Find requirements files
        path_obj = Path(path)
        requirements_files = []

        if path_obj.is_file() and path_obj.name in [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
        ]:
            requirements_files = [str(path_obj)]
        elif path_obj.is_dir():
            # Look for requirements files
            for req_file in ["requirements.txt", "requirements-dev.txt", "pyproject.toml"]:
                req_path = path_obj / req_file
                if req_path.exists():
                    requirements_files.append(str(req_path))

        if not requirements_files:
            # Safety can check installed packages without requirements file
            requirements_files = []

        try:
            # Build command
            cmd = ["safety", "check", "--json"]

            # Add requirements file if found
            if requirements_files:
                cmd.extend(["--file", requirements_files[0]])

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
                errors=["Safety execution timed out"],
                execution_time=60.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Safety error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse safety JSON output."""
        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        try:
            data = json.loads(output) if output.strip() else []

            for item in data:
                package = item.get("package", "unknown")
                vulnerability = item.get("vulnerability", "")
                installed_version = item.get("installed_version", "")
                affected_versions = item.get("affected_versions", "")
                cve = item.get("CVE", "")

                # Safety vulnerabilities are always high/critical
                severity = Severity.HIGH
                if "critical" in vulnerability.lower() or "critical" in str(item).lower():
                    severity = Severity.CRITICAL

                message = f"{package} {installed_version}: {vulnerability}"
                if cve:
                    message += f" (CVE: {cve})"
                if affected_versions:
                    message += f" [Affected: {affected_versions}]"

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=message,
                    file="requirements.txt",  # Safety checks dependencies
                    rule_id=cve or f"SAFETY-{package}",
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
            # Safety might output text format
            if output.strip():
                for line in output.split("\n"):
                    if line.strip() and "is vulnerable" in line.lower():
                        severity = Severity.HIGH
                        if "critical" in line.lower():
                            severity = Severity.CRITICAL

                        issue = LinterIssue(
                            linter=self.name,
                            severity=severity,
                            message=line.strip(),
                            file="requirements.txt",
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
