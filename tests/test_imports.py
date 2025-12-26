"""Test that all modules can be imported."""


def test_import_adapters():
    """Test adapter imports."""
    from codeoptix.adapters import create_adapter

    assert create_adapter is not None


def test_import_behaviors():
    """Test behavior imports."""
    from codeoptix.behaviors import create_behavior

    assert create_behavior is not None


def test_import_evaluation():
    """Test evaluation imports."""
    from codeoptix.evaluation import EvaluationEngine

    assert EvaluationEngine is not None


def test_import_reflection():
    """Test reflection imports."""
    from codeoptix.reflection import ReflectionEngine

    assert ReflectionEngine is not None


def test_import_evolution():
    """Test evolution imports."""
    from codeoptix.evolution import EvolutionEngine

    assert EvolutionEngine is not None


def test_import_artifacts():
    """Test artifact imports."""
    from codeoptix.artifacts import ArtifactManager

    assert ArtifactManager is not None


def test_import_cli():
    """Test CLI imports."""
    from codeoptix.cli import main

    assert main is not None
