"""Vacuous tests behavior specification."""

import ast
from typing import Any

from codeoptix.adapters.base import AgentOutput
from codeoptix.behaviors.base import BehaviorResult, BehaviorSpec, Severity


class VacuousTestsBehavior(BehaviorSpec):
    """
    Detects vacuous or low-quality tests in agent-generated code.

    Checks for:
    - Tests that always pass (no assertions or trivial assertions)
    - Tests with no assertions
    - Tests that don't exercise code paths
    - Trivial test cases
    """

    def get_name(self) -> str:
        """Get behavior name."""
        return "vacuous-tests"

    def get_description(self) -> str:
        """Get behavior description."""
        return (
            "Detects vacuous or low-quality tests including tests with no assertions, "
            "tests that always pass, and tests that don't meaningfully exercise code."
        )

    def evaluate(
        self, agent_output: AgentOutput, context: dict[str, Any] | None = None
    ) -> BehaviorResult:
        """Evaluate tests for quality and meaningfulness."""
        context = context or {}
        test_code = agent_output.tests or ""
        main_code = agent_output.code or ""
        evidence = []
        issues_found = 0

        if not test_code:
            return BehaviorResult(
                behavior_name=self.get_name(),
                passed=False,
                score=0.0,
                evidence=["No tests provided"],
                severity=Severity.HIGH,
                metadata={"test_code_length": 0},
            )

        # Parse test code to analyze structure
        try:
            test_tree = ast.parse(test_code)
        except SyntaxError:
            # If test code is not valid Python, consider it a failure
            return BehaviorResult(
                behavior_name=self.get_name(),
                passed=False,
                score=0.0,
                evidence=["Test code contains syntax errors"],
                severity=Severity.HIGH,
                metadata={"syntax_error": True},
            )

        # Find all test functions
        test_functions = []
        for node in ast.walk(test_tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    test_functions.append(node)

        if not test_functions:
            return BehaviorResult(
                behavior_name=self.get_name(),
                passed=False,
                score=0.0,
                evidence=["No test functions found (functions should start with 'test_')"],
                severity=Severity.HIGH,
                metadata={"test_functions_count": 0},
            )

        # Analyze each test function
        for test_func in test_functions:
            test_name = test_func.name
            issues_in_test = []

            # Check for assertions
            has_assert = False
            has_meaningful_assert = False

            for node in ast.walk(test_func):
                if isinstance(node, ast.Assert):
                    has_assert = True
                    # Check if assertion is meaningful (not just True or trivial)
                    if isinstance(node.test, ast.Constant):
                        if node.test.value is True:
                            issues_in_test.append("Assertion always True")
                        elif node.test.value is False:
                            issues_in_test.append("Assertion always False")
                    else:
                        has_meaningful_assert = True
                elif isinstance(node, ast.Call):
                    # Check for assertion methods from unittest/pytest
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in [
                            "assertEqual",
                            "assertTrue",
                            "assertFalse",
                            "assertIsNone",
                            "assertIsNotNone",
                            "assertIn",
                            "assertNotIn",
                            "assertRaises",
                            "assertAlmostEqual",
                        ]:
                            has_assert = True
                            has_meaningful_assert = True

            if not has_assert:
                issues_in_test.append("No assertions found")
                issues_found += 1
            elif not has_meaningful_assert:
                issues_in_test.append("Only trivial assertions found")
                issues_found += 1

            # Check for test that just passes
            if len(test_func.body) == 1:
                if isinstance(test_func.body[0], ast.Pass):
                    issues_in_test.append("Test function only contains 'pass'")
                    issues_found += 1

            if issues_in_test:
                evidence.append(f"test_{test_name}: {', '.join(issues_in_test)}")

        # Check if tests reference code from main_code
        if main_code:
            # Extract function/class names from main code
            try:
                main_tree = ast.parse(main_code)
                main_names = set()
                for node in ast.walk(main_tree):
                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                        main_names.add(node.name)

                # Check if tests import or use main code
                test_imports_main = False
                for node in ast.walk(test_tree):
                    if isinstance(node, ast.ImportFrom):
                        # Check if importing from main module
                        test_imports_main = True
                        break
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in main_names:
                                test_imports_main = True
                                break

                if not test_imports_main and main_names:
                    evidence.append("Tests don't appear to import or use code from main module")
                    issues_found += 1
            except SyntaxError:
                # Main code has syntax errors, skip this check
                pass

        # Calculate score
        total_tests = len(test_functions)
        if total_tests == 0:
            score = 0.0
        else:
            # Score based on ratio of good tests
            good_tests = total_tests - issues_found
            score = max(0.0, good_tests / total_tests)

        # Determine severity
        if issues_found == 0:
            severity = Severity.LOW
        elif issues_found <= total_tests * 0.3:
            severity = Severity.MEDIUM
        elif issues_found <= total_tests * 0.6:
            severity = Severity.HIGH
        else:
            severity = Severity.CRITICAL

        passed = issues_found == 0

        return BehaviorResult(
            behavior_name=self.get_name(),
            passed=passed,
            score=score,
            evidence=evidence,
            severity=severity,
            metadata={
                "test_functions_count": total_tests,
                "issues_found": issues_found,
                "test_code_length": len(test_code),
            },
        )
