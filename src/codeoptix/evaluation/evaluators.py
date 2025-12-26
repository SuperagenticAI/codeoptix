"""Evaluation components for CodeOptix."""

import subprocess
import tempfile
from pathlib import Path
from typing import Any


class StaticAnalyzer:
    """Static code analysis using bandit and other tools."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize static analyzer."""
        self.config = config or {}
        self.bandit_enabled = self.config.get("bandit", True)

    def analyze(self, code: str, output_path: Path | None = None) -> dict[str, Any]:
        """
        Run static analysis on code.

        Args:
            code: Code to analyze
            output_path: Optional path to save code file

        Returns:
            Dictionary with analysis results
        """
        results = {
            "bandit": None,
            "errors": [],
        }

        if not self.bandit_enabled:
            return results

        # Create temporary file with code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = Path(f.name)

        try:
            # Run bandit
            bandit_result = subprocess.run(
                ["bandit", "-f", "json", "-q", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if bandit_result.returncode == 0:
                import json

                try:
                    results["bandit"] = json.loads(bandit_result.stdout)
                except json.JSONDecodeError:
                    results["bandit"] = {"errors": ["Failed to parse bandit output"]}
            else:
                results["errors"].append(f"Bandit failed: {bandit_result.stderr}")
        except FileNotFoundError:
            results["errors"].append("Bandit not found in PATH")
        except subprocess.TimeoutExpired:
            results["errors"].append("Bandit analysis timed out")
        except Exception as e:
            results["errors"].append(f"Bandit error: {e!s}")
        finally:
            # Clean up
            temp_file.unlink()

        return results


class TestRunner:
    """Test execution and analysis using pytest."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize test runner."""
        self.config = config or {}
        self.coverage_enabled = self.config.get("coverage", True)

    def run_tests(self, code: str, tests: str, output_dir: Path | None = None) -> dict[str, Any]:
        """
        Run tests and collect results.

        Args:
            code: Main code to test
            tests: Test code
            output_dir: Optional directory for test artifacts

        Returns:
            Dictionary with test results
        """
        results = {
            "passed": False,
            "test_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "coverage": None,
            "errors": [],
        }

        if not tests:
            results["errors"].append("No tests provided")
            return results

        # Create temporary directory for test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write main code
            main_file = tmp_path / "main.py"
            main_file.write_text(code)

            # Write test file
            test_file = tmp_path / "test_main.py"
            test_file.write_text(tests)

            try:
                # Run pytest
                pytest_cmd = ["pytest", str(test_file), "-v", "--tb=short"]

                if self.coverage_enabled:
                    pytest_cmd.extend(
                        [
                            "--cov=main",
                            "--cov-report=json",
                            "--cov-report=term",
                        ]
                    )

                pytest_result = subprocess.run(
                    pytest_cmd,
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )

                # Parse pytest output
                results["passed"] = pytest_result.returncode == 0

                # Extract test counts from output
                output_lines = pytest_result.stdout.split("\n")
                for line in output_lines:
                    if "passed" in line.lower() and "failed" in line.lower():
                        # Try to extract numbers
                        import re

                        matches = re.findall(r"(\d+)\s+(?:passed|failed)", line)
                        if matches:
                            results["test_count"] = sum(int(m) for m in matches)
                            results["passed_count"] = int(matches[0]) if matches else 0
                            results["failed_count"] = int(matches[1]) if len(matches) > 1 else 0

                # Parse coverage if enabled
                if self.coverage_enabled:
                    coverage_file = tmp_path / "coverage.json"
                    if coverage_file.exists():
                        import json

                        try:
                            with open(coverage_file) as f:
                                coverage_data = json.load(f)
                                # Extract total coverage percentage
                                totals = coverage_data.get("totals", {})
                                results["coverage"] = {
                                    "percent_covered": totals.get("percent_covered", 0.0),
                                    "num_statements": totals.get("num_statements", 0),
                                    "missing_lines": totals.get("missing_lines", 0),
                                }
                        except (json.JSONDecodeError, KeyError):
                            pass

                if pytest_result.stderr:
                    results["errors"].append(f"Pytest stderr: {pytest_result.stderr[:200]}")

            except FileNotFoundError:
                results["errors"].append("Pytest not found in PATH")
            except subprocess.TimeoutExpired:
                results["errors"].append("Test execution timed out")
            except Exception as e:
                results["errors"].append(f"Test execution error: {e!s}")

        return results


class LLMEvaluator:
    """LLM-based evaluation for semantic analysis."""

    def __init__(self, llm_client, config: dict[str, Any] | None = None):
        """
        Initialize LLM evaluator.

        Args:
            llm_client: LLM client instance
            config: Optional configuration
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.model = self.config.get("model", "gpt-4o")

    def evaluate(
        self, code: str, behavior_description: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Use LLM to evaluate code against behavior description.

        Args:
            code: Code to evaluate
            behavior_description: Description of behavior to check
            context: Optional context

        Returns:
            Dictionary with LLM evaluation results
        """
        prompt = f"""Evaluate the following code for the behavior: {behavior_description}

Code:
```python
{code}
```

Provide:
1. Does the code exhibit this behavior? (yes/no)
2. Score from 0.0 to 1.0 (1.0 = perfect, 0.0 = severe issues)
3. Specific evidence or issues found

Format your response as:
BEHAVIOR_PRESENT: yes/no
SCORE: 0.0-1.0
EVIDENCE: [list of specific issues or confirmations]
"""

        try:
            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.3,  # Lower temperature for more consistent evaluation
            )

            # Parse response
            result = {
                "response": response,
                "behavior_present": None,
                "score": None,
                "evidence": [],
            }

            # Simple parsing (can be enhanced)
            if "BEHAVIOR_PRESENT:" in response:
                line = [l for l in response.split("\n") if "BEHAVIOR_PRESENT:" in l][0]
                result["behavior_present"] = "yes" in line.lower()

            if "SCORE:" in response:
                import re

                score_match = re.search(r"SCORE:\s*([\d.]+)", response)
                if score_match:
                    result["score"] = float(score_match.group(1))

            if "EVIDENCE:" in response:
                evidence_section = response.split("EVIDENCE:")[1] if "EVIDENCE:" in response else ""
                result["evidence"] = [
                    line.strip()
                    for line in evidence_section.split("\n")
                    if line.strip() and not line.strip().startswith("-")
                ]

            return result
        except Exception as e:
            return {
                "error": str(e),
                "behavior_present": None,
                "score": None,
            }


class ArtifactComparator:
    """Compare code against planning artifacts."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize artifact comparator."""
        self.config = config or {}

    def compare(self, code: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Compare code against planning artifacts.

        Args:
            code: Generated code
            artifacts: Planning artifacts (plan, requirements, api_spec, etc.)

        Returns:
            Dictionary with comparison results
        """
        results = {
            "alignment_score": 1.0,
            "missing_features": [],
            "extra_features": [],
            "deviations": [],
        }

        # This is a placeholder - actual implementation would use
        # more sophisticated comparison (LLM-based, AST-based, etc.)
        # For now, this is handled by plan-drift behavior spec

        return results
