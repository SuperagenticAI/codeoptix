"""Base classes for linter integration."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class LinterIssue:
    """Represents a single linter issue."""

    linter: str
    severity: Severity
    message: str
    file: str
    line: int | None = None
    column: int | None = None
    code: str | None = None
    rule_id: str | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "linter": self.linter,
            "severity": self.severity.value,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "code": self.code,
            "rule_id": self.rule_id,
            "confidence": self.confidence,
        }


@dataclass
class LinterResult:
    """Result from running a linter."""

    linter: str
    success: bool
    issues: list[LinterIssue]
    errors: list[str]
    execution_time: float
    raw_output: str | None = None

    @property
    def issue_count(self) -> int:
        """Get total issue count."""
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        """Get critical issue count."""
        return sum(1 for issue in self.issues if issue.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Get high severity issue count."""
        return sum(1 for issue in self.issues if issue.severity == Severity.HIGH)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "linter": self.linter,
            "success": self.success,
            "issue_count": self.issue_count,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "errors": self.errors,
            "execution_time": self.execution_time,
        }


class BaseLinter:
    """Base class for linter implementations."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize linter."""
        self.config = config or {}
        self.name = self.__class__.__name__.replace("Linter", "").lower()

    def is_available(self) -> bool:
        """Check if linter is available in PATH."""
        raise NotImplementedError

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run linter on code."""
        raise NotImplementedError

    def parse_output(self, output: str, stderr: str, returncode: int) -> LinterResult:
        """Parse linter output."""
        raise NotImplementedError
