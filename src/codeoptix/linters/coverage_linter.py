"""coverage.py test coverage linter integration."""

import subprocess
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class CoverageLinter(BaseLinter):
    """coverage.py test coverage analyzer."""

    def __init__(self, config: dict | None = None):
        """Initialize coverage linter."""
        super().__init__(config)
        self.name = "coverage"
        self.min_coverage = self.config.get("min_coverage", 80.0)

    def is_available(self) -> bool:
        """Check if coverage is available."""
        try:
            subprocess.run(
                ["coverage", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run coverage analysis."""
        import time

        start_time = time.time()

        if not self.is_available():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=["coverage not found in PATH. Install with: pip install coverage"],
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

        # Coverage needs to be run after tests
        # We'll check for existing coverage data or report
        coverage_data_file = path_obj / ".coverage"
        coverage_xml = path_obj / "coverage.xml"
        path_obj / "htmlcov"

        # Check if coverage data exists
        if not coverage_data_file.exists() and not coverage_xml.exists():
            return LinterResult(
                linter=self.name,
                success=True,
                issues=[],
                errors=["No coverage data found. Run tests with coverage first: pytest --cov"],
                execution_time=0.0,
            )

        try:
            # Generate report
            cmd = ["coverage", "report", "--format=total"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(path_obj) if path_obj.is_dir() else str(path_obj.parent),
                timeout=30,
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
                errors=["Coverage execution timed out"],
                execution_time=30.0,
            )
        except Exception as e:
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Coverage error: {e!s}"],
                execution_time=time.time() - start_time,
            )

    def parse_output(
        self,
        output: str,
        stderr: str,
        returncode: int,
        execution_time: float,
    ) -> LinterResult:
        """Parse coverage output."""
        import re

        issues = []
        errors = []

        if stderr:
            errors.append(stderr)

        # Parse coverage percentage
        # Coverage format: "TOTAL    XXX    XX%"
        pattern = r"TOTAL\s+\d+\s+(\d+)%"
        match = re.search(pattern, output)

        if match:
            coverage_percent = float(match.group(1))

            if coverage_percent < self.min_coverage:
                severity = Severity.HIGH if coverage_percent < 50 else Severity.MEDIUM

                issue = LinterIssue(
                    linter=self.name,
                    severity=severity,
                    message=f"Test coverage is {coverage_percent:.1f}%, below minimum {self.min_coverage}%",
                    file="coverage",
                    rule_id="COVERAGE-LOW",
                )
                issues.append(issue)
        else:
            # Try to parse from XML if available
            # Or just report that coverage was checked
            pass

        return LinterResult(
            linter=self.name,
            success=returncode == 0 and len(issues) == 0,
            issues=issues,
            errors=errors,
            execution_time=execution_time,
            raw_output=output,
        )
