"""Test CLI commands for coverage."""

from click.testing import CliRunner

from codeoptix.cli import main


class TestCLICommands:
    """Test CLI commands."""

    def test_eval_command_requires_agent(self):
        """Test eval command requires agent."""
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "--behaviors", "insecure-code"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_eval_command_requires_behaviors(self):
        """Test eval command requires behaviors."""
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "--agent", "claude-code"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_eval_command_invalid_agent(self):
        """Test eval command with invalid agent."""
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "--agent", "invalid", "--behaviors", "insecure-code"])
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "unknown" in result.output.lower()

    def test_eval_command_invalid_behavior(self):
        """Test eval command with invalid behavior."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["eval", "--agent", "claude-code", "--behaviors", "invalid-behavior"]
        )
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "unknown" in result.output.lower()
