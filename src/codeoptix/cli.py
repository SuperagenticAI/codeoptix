"""CLI interface for CodeOptiX."""

import asyncio
import json
import os
from pathlib import Path

import click
from acp import run_agent

from codeoptix.acp import (
    ACPAgentRegistry,
    ACPQualityBridge,
    CodeOptiXAgent,
    MultiAgentJudge,
)
from codeoptix.adapters.factory import create_adapter
from codeoptix.artifacts import ArtifactManager
from codeoptix.evaluation import EvaluationEngine
from codeoptix.evolution import EvolutionEngine
from codeoptix.linters import LinterRunner
from codeoptix.reflection import ReflectionEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client


@click.group()
@click.version_option(version="0.1.3")
def main():
    """CodeOptiX - Agentic Code Optimization & Deep Evaluation for Superior Coding Agent Experience.

    The universal code optimization engine that improves coding agent experience with deep evaluations and optimization. When AI coding agents dazzle with impressive code but leave you wondering about quality, maintainability, security, and reliability, CodeOptiX ensures proper behavior through evaluations, reflection, and self-improvement.

    Built by Superagentic AI - Advancing AI agent optimization and autonomous systems.
    """


@main.command()
@click.option("--agent", required=True, help="Agent type (claude-code, codex, gemini-cli)")
@click.option(
    "--behaviors",
    required=True,
    help="Comma-separated behavior names (e.g., insecure-code,vacuous-tests)",
)
@click.option("--output", default="results.json", help="Output file for results")
@click.option("--config", type=click.Path(exists=True), help="Path to config file (JSON/YAML)")
@click.option(
    "--llm-provider",
    default="openai",
    help="LLM provider for evaluation (anthropic, openai, google, ollama)",
)
@click.option("--llm-api-key", help="API key for LLM (or set environment variable)")
@click.option(
    "--context",
    type=click.Path(exists=True),
    help="Path to context file (JSON) with plan/requirements",
)
@click.option(
    "--fail-on-failure", is_flag=True, help="Exit with non-zero code if any behavior fails"
)
def eval(agent, behaviors, output, config, llm_provider, llm_api_key, context, fail_on_failure):
    """Evaluate agent against behavior specifications."""
    import sys

    click.echo("🔍 CodeOptiX Evaluation")
    click.echo("=" * 60)

    # Parse behaviors
    behavior_list = [b.strip() for b in behaviors.split(",") if b.strip()]

    if not behavior_list:
        click.echo(
            "❌ Error: No behaviors specified. Please provide at least one behavior.", err=True
        )
        click.echo("   Example: --behaviors insecure-code", err=True)
        click.echo(
            "   Available behaviors: insecure-code, vacuous-tests, plan-drift",
            err=True,
        )
        sys.exit(1)

    # Validate behavior names (keep in sync with evaluation engine)
    valid_behaviors = [
        "insecure-code",
        "vacuous-tests",
        "plan-drift",
        "api-smoke",
        "contract-compliance",
        "db-validation",
    ]
    invalid_behaviors = [b for b in behavior_list if b not in valid_behaviors]
    if invalid_behaviors:
        click.echo(f"❌ Error: Invalid behavior name(s): {', '.join(invalid_behaviors)}", err=True)
        click.echo(f"   Available behaviors: {', '.join(valid_behaviors)}", err=True)
        sys.exit(1)

    click.echo(f"📊 Agent: {agent}")
    click.echo(f"📋 Behavior(s): {', '.join(behavior_list)}")
    if len(behavior_list) == 1:
        click.echo("   [INFO] Single behavior mode - perfect for getting started!")

    # Load config if provided
    eval_config = {}
    if config:
        config_path = Path(config)
        if not config_path.exists():
            click.echo(f"❌ Error: Config file not found: {config}", err=True)
            click.echo("   Please check the file path and try again.", err=True)
            sys.exit(1)

        try:
            if config_path.suffix == ".json":
                with open(config_path) as f:
                    eval_config = json.load(f)
            elif config_path.suffix in [".yaml", ".yml"]:
                import yaml

                with open(config_path) as f:
                    eval_config = yaml.safe_load(f)
            else:
                click.echo(
                    f"❌ Error: Unsupported config file format: {config_path.suffix}", err=True
                )
                click.echo("   Supported formats: .json, .yaml, .yml", err=True)
                sys.exit(1)
        except json.JSONDecodeError as e:
            click.echo(f"❌ Error: Invalid JSON in config file: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: Failed to load config file: {e}", err=True)
            sys.exit(1)

    # Load context if provided
    eval_context = {}
    if context:
        context_path = Path(context)
        if not context_path.exists():
            click.echo(f"❌ Error: Context file not found: {context}", err=True)
            sys.exit(1)
        try:
            with open(context_path) as f:
                eval_context = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(f"❌ Error: Invalid JSON in context file: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: Failed to load context file: {e}", err=True)
            sys.exit(1)

    # Normalize provider name and decide if we need an API key
    llm_provider = (
        eval_config.get("llm_provider")
        or llm_provider
        or os.getenv("CODEOPTIX_LLM_PROVIDER", "openai")
    ).lower()
    is_ollama = llm_provider == "ollama"

    # Create adapter
    adapter_config = eval_config.get("adapter", {})
    if not adapter_config.get("llm_config"):
        # Default LLM config
        api_key = llm_api_key or os.getenv(f"{llm_provider.upper()}_API_KEY")
        if not api_key and not is_ollama:
            click.echo(f"❌ Error: API key required for {llm_provider}", err=True)
            click.echo(
                f"   Set {llm_provider.upper()}_API_KEY environment variable or use --llm-api-key",
                err=True,
            )
            click.echo("", err=True)
            click.echo("💡 Tip: Without an API key, you can use basic static analysis:", err=True)
            click.echo("   codeoptix lint --path ./src", err=True)
            click.echo(
                "   This runs linters (ruff, bandit, flake8, etc.) without requiring API keys.",
                err=True,
            )
            sys.exit(1)

        adapter_config["llm_config"] = {
            "provider": llm_provider,
            # Ollama does not need an API key; other providers still do.
            "api_key": api_key if not is_ollama else None,
        }

    try:
        adapter = create_adapter(agent, adapter_config)
        click.echo(f"✅ Adapter created: {adapter.get_adapter_type()}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo("   Available agents: claude-code, codex, gemini-cli", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: Failed to create adapter: {e}", err=True)
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            click.echo(
                "   💡 Tip: Check your API key is correct and has sufficient credits", err=True
            )
        sys.exit(1)

    # Create LLM client for evaluation
    if not is_ollama:
        click.echo("🧠 Using local Ollama provider.")

    try:
        llm_config = adapter_config["llm_config"]
        llm_client = create_llm_client(
            LLMProvider(llm_config["provider"]), llm_config.get("api_key"), llm_config.get("model")
        )
    except Exception as e:
        click.echo(f"❌ Error: Failed to create LLM client: {e}", err=True)
        if "api_key" in str(e).lower():
            click.echo("   💡 Tip: Verify your API key is correct", err=True)
        if is_ollama:
            click.echo(
                "   💡 Tip: Ensure `ollama serve` is running and the model is pulled (e.g. `ollama pull gpt-oss:120b`).",
                err=True,
            )
        sys.exit(1)

    # Create evaluation engine
    eval_engine_config = eval_config.get("evaluation", {})
    try:
        eval_engine = EvaluationEngine(adapter, llm_client, config=eval_engine_config)
    except Exception as e:
        click.echo(f"❌ Error: Failed to create evaluation engine: {e}", err=True)
        sys.exit(1)

    # Run evaluation
    click.echo("\n🚀 Running evaluation...")
    try:
        results = eval_engine.evaluate_behaviors(behavior_names=behavior_list, context=eval_context)

        if not results or "behaviors" not in results:
            click.echo("❌ Error: Evaluation returned no results", err=True)
            click.echo("   This might indicate an issue with the evaluation engine", err=True)
            sys.exit(1)

        # Save results
        artifact_manager = ArtifactManager()
        results_file = artifact_manager.save_results(results)

        # Also save to specified output if different
        if output != str(results_file.name):
            try:
                with open(output, "w") as f:
                    json.dump(results, f, indent=2, default=str)
            except Exception as e:
                click.echo(f"⚠️  Warning: Failed to save to {output}: {e}", err=True)
                click.echo(f"   Results saved to: {results_file}", err=True)

        click.echo("\n" + "=" * 60)
        click.echo("✅ Evaluation Complete!")
        click.echo("=" * 60)
        click.echo(f"📊 Overall Score: {results.get('overall_score', 0.0):.2%}")
        click.echo(f"📁 Results: {results_file}")
        click.echo(f"🆔 Run ID: {results.get('run_id', 'unknown')}")

        # Show behavior results
        behaviors_data = results.get("behaviors", {})
        if behaviors_data:
            click.echo("\n📋 Behavior Results:")
            for behavior_name, behavior_data in behaviors_data.items():
                passed = behavior_data.get("passed", True)
                score = behavior_data.get("score", 0.0)
                emoji = "✅" if passed else "❌"
                click.echo(f"   {emoji} {behavior_name}: {score:.2%}")

        # Check for failures if --fail-on-failure is set
        if fail_on_failure:
            failed_behaviors = [
                name for name, data in behaviors_data.items() if not data.get("passed", True)
            ]

            if failed_behaviors:
                click.echo(
                    f"\n❌ {len(failed_behaviors)} behavior(s) failed: {', '.join(failed_behaviors)}",
                    err=True,
                )
                click.echo("   Exiting with error code (--fail-on-failure)", err=True)
                sys.exit(1)
            else:
                click.echo("\n✅ All behaviors passed!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Evaluation interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: Evaluation failed: {e}", err=True)
        if hasattr(e, "__cause__") and e.__cause__:
            click.echo(f"   Caused by: {e.__cause__!s}", err=True)
        click.echo("\n💡 Troubleshooting tips:", err=True)
        click.echo("   - Check your API key is valid and has credits", err=True)
        click.echo("   - Verify the agent type is correct", err=True)
        click.echo("   - Try with a single behavior first: --behaviors insecure-code", err=True)
        click.echo("   - Check the documentation: https://codeoptix.ai/docs", err=True)
        sys.exit(1)


@main.command()
@click.option("--input", required=True, help="Path to results JSON file or run ID")
@click.option("--output", help="Output file for reflection (default: reflection_{run_id}.md)")
@click.option("--agent-name", help="Agent name for reflection report")
def reflect(input, output, agent_name):
    """Generate reflection report from evaluation results."""
    click.echo("📝 Generating reflection report...")

    artifact_manager = ArtifactManager()

    # Load results
    input_path = Path(input)
    if input_path.exists():
        # Load from file
        with open(input_path) as f:
            results = json.load(f)
        run_id = results.get("run_id")
    else:
        # Assume it's a run ID
        run_id = input
        try:
            results = artifact_manager.load_results(run_id)
        except FileNotFoundError:
            click.echo(f"❌ Results not found for run ID: {run_id}", err=True)
            raise click.Abort()

    # Generate reflection
    reflection_engine = ReflectionEngine(artifact_manager)

    try:
        reflection = reflection_engine.reflect(results=results, agent_name=agent_name, save=True)

        # Save to specified output if provided
        if output:
            with open(output, "w") as f:
                f.write(reflection)
            click.echo(f"✅ Reflection saved to: {output}")
        else:
            reflection_file = artifact_manager.artifacts_dir / f"reflection_{run_id}.md"
            click.echo(f"✅ Reflection saved to: {reflection_file}")

        click.echo(f"   Run ID: {run_id}")

    except Exception as e:
        click.echo(f"❌ Reflection generation failed: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option("--input", required=True, help="Path to results JSON file or run ID")
@click.option(
    "--reflection", help="Path to reflection markdown file (auto-generated if not provided)"
)
@click.option(
    "--output", help="Output file for evolved prompts (default: evolved_prompts_{run_id}.yaml)"
)
@click.option("--iterations", default=3, help="Number of evolution iterations")
@click.option("--config", type=click.Path(exists=True), help="Path to config file (JSON/YAML)")
@click.option(
    "--llm-provider",
    default="openai",
    help="LLM provider for evolution (anthropic, openai, google, ollama)",
)
@click.option("--llm-api-key", help="API key for LLM (or set environment variable)")
def evolve(input, reflection, output, iterations, config, llm_provider, llm_api_key):
    """Evolve agent prompts based on evaluation results."""
    click.echo("🧬 Evolving agent prompts...")

    artifact_manager = ArtifactManager()

    # Load results
    input_path = Path(input)
    if input_path.exists():
        with open(input_path) as f:
            results = json.load(f)
        run_id = results.get("run_id")
    else:
        run_id = input
        try:
            results = artifact_manager.load_results(run_id)
        except FileNotFoundError:
            click.echo(f"❌ Results not found for run ID: {run_id}", err=True)
            raise click.Abort()

    # Load or generate reflection
    if reflection:
        reflection_path = Path(reflection)
        if reflection_path.exists():
            with open(reflection_path) as f:
                reflection_content = f.read()
        else:
            click.echo("⚠️  Reflection file not found, generating...")
            reflection_engine = ReflectionEngine(artifact_manager)
            reflection_content = reflection_engine.reflect_from_run_id(run_id)
    else:
        # Auto-generate reflection
        click.echo("📝 Generating reflection...")
        reflection_engine = ReflectionEngine(artifact_manager)
        reflection_content = reflection_engine.reflect_from_run_id(run_id)

    # Load config
    evolve_config = {}
    if config:
        config_path = Path(config)
        if config_path.suffix == ".json":
            with open(config_path) as f:
                evolve_config = json.load(f)
        elif config_path.suffix in [".yaml", ".yml"]:
            import yaml

            with open(config_path) as f:
                evolve_config = yaml.safe_load(f)

    # Set iterations
    evolution_config = evolve_config.get("evolution", {})
    evolution_config["max_iterations"] = iterations

    # Get agent type and config from results
    metadata = results.get("metadata", {})
    agent_type = metadata.get("agent", "claude-code")

    # Get LLM provider from command line or config
    if llm_provider == "openai":  # default, check config
        llm_provider = evolve_config.get("llm_provider", "openai")
    # llm_api_key param takes precedence, then config, then env
    llm_api_key = (
        llm_api_key
        or evolve_config.get("llm_api_key")
        or os.getenv(f"{llm_provider.upper()}_API_KEY")
    )

    is_ollama = llm_provider == "ollama"
    if not llm_api_key and not is_ollama:
        click.echo(
            f"❌ LLM API key required. Set {llm_provider.upper()}_API_KEY or use --config", err=True
        )
        click.echo("", err=True)
        click.echo("💡 Tip: Without an API key, you can use basic static analysis:", err=True)
        click.echo("   codeoptix lint --path ./src", err=True)
        click.echo(
            "   This runs linters (ruff, bandit, flake8, etc.) without requiring API keys.",
            err=True,
        )
        raise click.Abort()

    try:
        # Create adapter
        adapter_config = evolve_config.get("adapter", {})
        if not adapter_config.get("llm_config"):
            adapter_config["llm_config"] = {
                "provider": llm_provider,
                "api_key": llm_api_key,
            }

        adapter = create_adapter(agent_type, adapter_config)
        click.echo(f"✅ Created adapter: {adapter.get_adapter_type()}")

        # Create LLM client (use same config as adapter for consistency)
        llm_config = adapter_config["llm_config"]
        llm_client = create_llm_client(
            LLMProvider(llm_config["provider"]), llm_config.get("api_key"), llm_config.get("model")
        )

        # Create evaluation engine
        eval_engine_config = evolve_config.get("evaluation", {})
        eval_engine = EvaluationEngine(adapter, llm_client, config=eval_engine_config)

        # Create evolution engine
        evolution_engine = EvolutionEngine(
            adapter=adapter,
            evaluation_engine=eval_engine,
            llm_client=llm_client,
            artifact_manager=artifact_manager,
            config=evolution_config,
        )

        # Run evolution
        click.echo(f"🧬 Running evolution ({iterations} iterations)...")
        evolved = evolution_engine.evolve(
            evaluation_results=results,
            reflection=reflection_content,
            behavior_names=list(results.get("behaviors", {}).keys()),
        )

        # Save to specified output if provided
        if output:
            import yaml

            with open(output, "w") as f:
                yaml.dump(evolved, f, default_flow_style=False, sort_keys=False)
            click.echo(f"✅ Evolved prompts saved to: {output}")
        else:
            evolved_file = artifact_manager.artifacts_dir / f"evolved_prompts_{run_id}.yaml"
            click.echo(f"✅ Evolved prompts saved to: {evolved_file}")

        click.echo(f"   Improvement: {evolved['metadata']['improvement']:.2f}")
        click.echo(f"   Final score: {evolved['metadata']['final_score']:.2f}/1.0")
        click.echo(f"   Run ID: {run_id}")

    except Exception as e:
        click.echo(f"❌ Evolution failed: {e}", err=True)
        import traceback

        click.echo(traceback.format_exc(), err=True)
        raise click.Abort()


@main.command()
@click.option("--agent", required=True, help="Agent type")
@click.option("--behaviors", required=True, help="Comma-separated behavior names")
@click.option("--evolve", is_flag=True, help="Run evolution after evaluation")
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
def run(agent, behaviors, evolve, config):
    """Run full pipeline: evaluate → reflect → evolve (optional)."""
    click.echo("🚀 Running full CodeOptiX pipeline...")

    # Step 1: Evaluate
    click.echo("\n" + "=" * 60)
    click.echo("STEP 1: Evaluation")
    click.echo("=" * 60)

    # Create temporary results file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_results = f.name

    try:
        # Run eval command
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(
            eval,
            [
                "--agent",
                agent,
                "--behaviors",
                behaviors,
                "--output",
                temp_results,
                "--config",
                config if config else "",
            ],
        )

        if result.exit_code != 0:
            click.echo(f"❌ Evaluation failed: {result.output}", err=True)
            raise click.Abort()

        # Step 2: Reflect
        click.echo("\n" + "=" * 60)
        click.echo("STEP 2: Reflection")
        click.echo("=" * 60)

        result = runner.invoke(
            reflect,
            [
                "--input",
                temp_results,
            ],
        )

        if result.exit_code != 0:
            click.echo(f"❌ Reflection failed: {result.output}", err=True)
            raise click.Abort()

        # Step 3: Evolve (if requested)
        if evolve:
            click.echo("\n" + "=" * 60)
            click.echo("STEP 3: Evolution")
            click.echo("=" * 60)

            result = runner.invoke(
                evolve,
                [
                    "--input",
                    temp_results,
                ],
            )

            if result.exit_code != 0:
                click.echo(f"⚠️  Evolution failed: {result.output}", err=True)

        click.echo("\n" + "=" * 60)
        click.echo("✅ Pipeline complete!")
        click.echo("=" * 60)

    finally:
        # Clean up temp file
        if os.path.exists(temp_results):
            os.unlink(temp_results)


@main.command()
@click.option("--agent", required=True, help="Agent type (claude-code, codex, gemini-cli)")
@click.option(
    "--behaviors", required=True, help="Comma-separated behavior names (e.g., insecure-code)"
)
@click.option("--config", type=click.Path(exists=True), help="Path to config file (JSON/YAML)")
@click.option(
    "--llm-provider",
    default="openai",
    help="LLM provider for evaluation (anthropic, openai, google, ollama)",
)
@click.option("--llm-api-key", help="API key for LLM (or set environment variable)")
@click.option(
    "--fail-on-failure",
    is_flag=True,
    default=True,
    help="Exit with non-zero code if any behavior fails (default: true)",
)
@click.option(
    "--output-format",
    default="json",
    type=click.Choice(["json", "summary"]),
    help="Output format (default: json)",
)
def ci(agent, behaviors, config, llm_provider, llm_api_key, fail_on_failure, output_format):
    """
    Run CodeOptiX in CI/CD mode.

    Optimized for CI/CD pipelines with:
    - Non-interactive execution
    - Exit codes for automation
    - Summary output format
    - Fail-fast behavior
    """
    import sys

    click.echo("🔍 CodeOptiX CI/CD Check")
    click.echo("=" * 60)

    # Parse behaviors
    behavior_list = [b.strip() for b in behaviors.split(",")]

    if not behavior_list:
        click.echo("❌ Error: At least one behavior must be specified", err=True)
        sys.exit(1)

    # Load config if provided
    config_dict = {}
    if config:
        config_path = Path(config)
        if config_path.suffix == ".json":
            with open(config_path) as f:
                config_dict = json.load(f)
        elif config_path.suffix in [".yaml", ".yml"]:
            import yaml

            with open(config_path) as f:
                config_dict = yaml.safe_load(f)

    # Get API key
    api_key = llm_api_key or os.getenv(f"{llm_provider.upper()}_API_KEY")
    if not api_key:
        click.echo(
            f"❌ Error: API key required. Set {llm_provider.upper()}_API_KEY environment variable or use --llm-api-key",
            err=True,
        )
        click.echo("", err=True)
        click.echo("💡 Tip: Without an API key, you can use basic static analysis:", err=True)
        click.echo("   codeoptix lint --path ./src", err=True)
        click.echo(
            "   This runs linters (ruff, bandit, flake8, etc.) without requiring API keys.",
            err=True,
        )
        sys.exit(1)

    try:
        # Create adapter
        adapter_config = config_dict.get("adapter", {})
        if not adapter_config.get("llm_config"):
            adapter_config["llm_config"] = {
                "provider": llm_provider,
                "api_key": api_key,
            }

        adapter = create_adapter(agent, adapter_config)

        # Create LLM client
        llm_provider_enum = LLMProvider[llm_provider.upper()]
        llm_client = create_llm_client(llm_provider_enum, api_key=api_key)

        # Create evaluation engine
        eval_config = config_dict.get("evaluation", {})
        eval_engine = EvaluationEngine(adapter, llm_client, config=eval_config)

        # Run evaluation
        click.echo(f"📊 Evaluating {len(behavior_list)} behavior(s): {', '.join(behavior_list)}")

        results = eval_engine.evaluate_behaviors(
            behavior_names=behavior_list, context=config_dict.get("context", {})
        )

        # Save results
        artifact_manager = ArtifactManager()
        run_id = artifact_manager.save_results(results)

        # Display results
        overall_score = results.get("overall_score", 0.0)
        behaviors_data = results.get("behaviors", {})

        if output_format == "summary":
            click.echo("\n" + "=" * 60)
            click.echo("📊 Evaluation Summary")
            click.echo("=" * 60)
            click.echo(f"Overall Score: {overall_score:.2%}")
            click.echo(f"Run ID: {run_id}")
            click.echo()

            for behavior_name, behavior_data in behaviors_data.items():
                passed = behavior_data.get("passed", True)
                score = behavior_data.get("score", 0.0)
                emoji = "✅" if passed else "❌"
                click.echo(f"{emoji} {behavior_name}: {score:.2%}")

                if not passed and behavior_data.get("evidence"):
                    evidence = behavior_data["evidence"][:3]
                    for ev in evidence:
                        click.echo(f"   ⚠️  {ev}")
            click.echo("=" * 60)
        else:
            # JSON output
            click.echo(
                json.dumps(
                    {
                        "run_id": run_id,
                        "overall_score": overall_score,
                        "behaviors": {
                            name: {
                                "passed": data.get("passed", True),
                                "score": data.get("score", 0.0),
                                "evidence": data.get("evidence", [])[:3],
                            }
                            for name, data in behaviors_data.items()
                        },
                    },
                    indent=2,
                )
            )

        # Check for failures
        failed_behaviors = [
            name for name, data in behaviors_data.items() if not data.get("passed", True)
        ]

        if failed_behaviors:
            if fail_on_failure:
                click.echo(
                    f"\n❌ {len(failed_behaviors)} behavior(s) failed: {', '.join(failed_behaviors)}",
                    err=True,
                )
                sys.exit(1)
            else:
                click.echo(
                    f"\n⚠️  {len(failed_behaviors)} behavior(s) failed: {', '.join(failed_behaviors)}",
                    err=True,
                )
        else:
            click.echo("\n✅ All behaviors passed!")

    except Exception as e:
        click.echo(f"❌ Error: {e!s}", err=True)
        if hasattr(e, "__cause__") and e.__cause__:
            click.echo(f"   Caused by: {e.__cause__!s}", err=True)
        sys.exit(1)


def _get_install_command(linter_name: str) -> str | None:
    """Get install command for a linter."""
    install_commands = {
        "bandit": "pip install bandit",
        "pylint": "pip install pylint",
        "flake8": "pip install flake8",
        "ruff": "pip install ruff or uv tool install ruff",
        "mypy": "pip install mypy",
        "safety": "pip install safety",
        "pip-audit": "pip install pip-audit",
        "coverage": "pip install coverage",
        "html-accessibility": "No installation needed (built-in)",
    }
    return install_commands.get(linter_name)


@main.command()
@click.option("--path", type=click.Path(exists=True), help="Path to code (file or directory)")
@click.option(
    "--linters", help="Comma-separated linter names (default: auto-detect from language and config)"
)
@click.option(
    "--output",
    default="summary",
    type=click.Choice(["json", "summary"]),
    help="Output format (default: summary)",
)
@click.option("--fail-on-issues", is_flag=True, help="Exit with non-zero code if issues found")
@click.option(
    "--no-auto-detect", is_flag=True, help="Disable auto-detection of language and linters"
)
@click.option("--list-linters", is_flag=True, help="List all available linters and exit")
def lint(path, linters, output, fail_on_issues, no_auto_detect, list_linters):
    """
    Run linters on code (no API key required).

    This command runs static analysis linters on your code without requiring
    any API keys. Perfect for quick code quality checks.

    Examples:
        codeoptix lint --path ./src
        codeoptix lint --path ./src --linters bandit,flake8
        codeoptix lint --path ./src --output summary
    """
    import sys

    # List linters if requested (check this first, before path validation)
    if list_linters:
        runner = LinterRunner()
        available = runner.get_available_linters()
        all_linters = runner.get_all_linters()

        click.echo("Available Linters (Zero New Dependencies):")
        click.echo("=" * 60)
        click.echo("\nCode Quality:")
        for linter in ["ruff", "pylint", "flake8"]:
            status = "✅" if linter in available else "❌"
            click.echo(f"  {status} {linter}")

        click.echo("\nType Checking:")
        for linter in ["mypy"]:
            status = "✅" if linter in available else "❌"
            click.echo(f"  {status} {linter}")

        click.echo("\nSecurity:")
        for linter in ["bandit", "safety", "pip-audit"]:
            status = "✅" if linter in available else "❌"
            click.echo(f"  {status} {linter}")

        click.echo("\nTesting:")
        for linter in ["coverage"]:
            status = "✅" if linter in available else "❌"
            click.echo(f"  {status} {linter}")

        click.echo("\nAccessibility:")
        for linter in ["html-accessibility"]:
            status = "✅" if linter in available else "❌"
            click.echo(f"  {status} {linter} (custom, no dependency)")

        click.echo(f"\nTotal: {len(available)}/{len(all_linters)} linters available")
        click.echo("\nInstall missing linters:")
        for linter in all_linters:
            if linter not in available:
                cmd = _get_install_command(linter)
                if cmd:
                    click.echo(f"  {cmd}")
        return

    if not path:
        click.echo("❌ Error: --path is required (or use --list-linters)", err=True)
        sys.exit(1)

    click.echo("🔍 CodeOptiX Linter Check")
    click.echo("=" * 60)
    click.echo(f"📁 Path: {path}")

    try:
        # Create linter runner
        runner = LinterRunner()

        # Auto-detect or use specified linters
        if linters:
            linter_list = [l.strip() for l in linters.split(",") if l.strip()]
        else:
            # Auto-detect from language and existing configs
            # Find Python files if directory
            from pathlib import Path

            from codeoptix.linters.language_detector import LanguageDetector

            path_obj = Path(path)
            if path_obj.is_dir():
                python_files = list(path_obj.rglob("*.py"))[:10]  # Sample first 10
                file_paths = [str(f) for f in python_files]
            elif path_obj.is_file() and path_obj.suffix == ".py":
                file_paths = [str(path_obj)]
            else:
                file_paths = []

            # Detect language and find configs
            if file_paths:
                detected_languages = LanguageDetector.detect_languages(file_paths)
                config_files = LanguageDetector.find_config_files(path)

                click.echo(
                    f"🌐 Detected languages: {', '.join(detected_languages) if detected_languages else 'unknown'}"
                )

                # Get recommended linters
                linter_list = []
                for lang in detected_languages:
                    linter_list.extend(LanguageDetector.get_linters_for_language(lang))

                # Prioritize linters with existing configs
                configured_linters = [l for l in linter_list if l in config_files]
                if configured_linters:
                    linter_list = configured_linters + [
                        l for l in linter_list if l not in configured_linters
                    ]

                # Remove duplicates while preserving order
                seen = set()
                linter_list = [l for l in linter_list if not (l in seen or seen.add(l))]

                if not linter_list:
                    # Fallback to common Python linters
                    linter_list = ["ruff", "bandit"]  # Ruff first (fastest)
            else:
                linter_list = ["ruff", "bandit"]  # Default for non-Python

        click.echo(f"🔧 Linters: {', '.join(linter_list) if linter_list else 'auto-detect'}")

        # Check available linters
        available = runner.get_available_linters()
        all_linters = runner.get_all_linters()
        requested_available = [l for l in linter_list if l in available]

        if not requested_available:
            click.echo("❌ Error: No requested linters are available", err=True)
            click.echo(f"   Available linters: {', '.join(available)}", err=True)
            click.echo("   Install missing linters:", err=True)
            for linter in linter_list:
                if linter not in available:
                    install_cmd = _get_install_command(linter)
                    if install_cmd:
                        click.echo(f"     {install_cmd}", err=True)
            sys.exit(1)

        if len(requested_available) < len(linter_list):
            missing = [l for l in linter_list if l not in available]
            click.echo(f"⚠️  Warning: Some linters not available: {', '.join(missing)}", err=True)
            click.echo("   These linters will be skipped. Install them to use:", err=True)
            for linter in missing:
                install_cmd = _get_install_command(linter)
                if install_cmd:
                    click.echo(f"     {install_cmd}", err=True)

        # Run linters
        click.echo("🚀 Running linters...")
        results = runner.run_linters(
            path,
            linter_names=requested_available if requested_available else None,
            auto_detect=not no_auto_detect,
        )

        # Display results
        summary = results.get("summary", {})
        total_issues = summary.get("total_issues", 0)

        if output == "summary":
            click.echo("\n" + "=" * 60)
            click.echo("📊 Linter Results Summary")
            click.echo("=" * 60)
            click.echo(f"Total Issues: {total_issues}")
            click.echo(f"  Critical: {summary.get('critical', 0)}")
            click.echo(f"  High: {summary.get('high', 0)}")
            click.echo(f"  Medium: {summary.get('medium', 0)}")
            click.echo(f"  Low: {summary.get('low', 0)}")
            click.echo(f"\nExecution Time: {results.get('execution_time', 0):.2f}s")

            # Show issues by linter
            linter_results = results.get("results", {})
            for linter_name, linter_result in linter_results.items():
                if isinstance(linter_result, dict):
                    issue_count = linter_result.get("issue_count", 0)
                    if issue_count > 0:
                        click.echo(f"\n{linter_name}: {issue_count} issue(s)")

            # Show top issues
            issues = results.get("issues", [])
            if issues:
                click.echo("\n⚠️  Top Issues:")
                for issue in issues[:10]:  # Show top 10
                    severity = issue.get("severity", "low").upper()
                    file = issue.get("file", "unknown")
                    line = issue.get("line", "?")
                    message = issue.get("message", "Unknown")
                    click.echo(f"   [{severity}] {file}:{line} - {message}")

            click.echo("=" * 60)
        else:
            # JSON output
            click.echo(json.dumps(results, indent=2, default=str))

        # Check for failures
        if results.get("errors"):
            click.echo("\n⚠️  Errors:", err=True)
            for error in results["errors"]:
                click.echo(f"   {error}", err=True)

        if total_issues > 0:
            if fail_on_issues:
                click.echo(f"\n❌ Found {total_issues} issue(s)", err=True)
                sys.exit(1)
            else:
                click.echo(f"\n⚠️  Found {total_issues} issue(s)")
        else:
            click.echo("\n✅ No issues found!")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, "__cause__") and e.__cause__:
            click.echo(f"   Caused by: {e.__cause__!s}", err=True)
        sys.exit(1)


@main.command()
@click.option("--base", default="main", help="Base branch (default: main)")
@click.option("--head", help="Head branch or commit (default: current branch)")
@click.option(
    "--linters", help="Comma-separated linter names (default: auto-detect from language and config)"
)
@click.option(
    "--output", default="summary", type=click.Choice(["json", "summary"]), help="Output format"
)
@click.option("--fail-on-issues", is_flag=True, help="Exit with non-zero code if issues found")
@click.option(
    "--no-auto-detect", is_flag=True, help="Disable auto-detection of language and linters"
)
def check(base, head, linters, output, fail_on_issues, no_auto_detect):
    """
    Check code changes in git (no API key required).

    This command analyzes code changes between git branches/commits using
    linters. Perfect for CI/CD pipelines and PR checks.

    Examples:
        codeoptix check --base main --head feature-branch
        codeoptix check --base main --head HEAD
        codeoptix check --linters bandit,flake8
    """
    import subprocess
    import sys

    click.echo("🔍 CodeOptiX Git Check")
    click.echo("=" * 60)

    # Get git diff
    try:
        # Determine head
        if not head:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            head = result.stdout.strip()

        click.echo(f"📊 Comparing: {base}..{head}")

        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", base, head],
            capture_output=True,
            text=True,
            check=True,
        )

        changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        if not changed_files:
            click.echo("✅ No files changed")
            return

        # Filter Python files
        python_files = [f for f in changed_files if f.endswith(".py")]

        if not python_files:
            click.echo("ℹ️  No Python files changed")
            return

        click.echo(f"📝 Changed Python files: {len(python_files)}")
        click.echo()

        # Auto-detect or use specified linters
        from codeoptix.linters.language_detector import LanguageDetector

        if linters:
            linter_list = [l.strip() for l in linters.split(",") if l.strip()]
        else:
            # Auto-detect from changed files
            detected_languages = LanguageDetector.detect_languages(python_files)
            config_files = LanguageDetector.find_config_files(".")

            click.echo(
                f"🌐 Detected languages: {', '.join(detected_languages) if detected_languages else 'Python'}"
            )

            # Get recommended linters
            linter_list = []
            for lang in detected_languages:
                linter_list.extend(LanguageDetector.get_linters_for_language(lang))

            # Prioritize linters with existing configs
            configured_linters = [l for l in linter_list if l in config_files]
            if configured_linters:
                linter_list = configured_linters + [
                    l for l in linter_list if l not in configured_linters
                ]

            # Remove duplicates
            seen = set()
            linter_list = [l for l in linter_list if not (l in seen or seen.add(l))]

            if not linter_list:
                linter_list = ["ruff", "bandit"]  # Default

        click.echo(f"🔧 Linters: {', '.join(linter_list)}")

        # Run linters on changed files
        runner = LinterRunner()

        # Get current directory as base path
        import os

        base_path = os.getcwd()

        results = runner.run_linters(
            base_path,
            linter_names=linter_list,
            files=python_files,
            auto_detect=not no_auto_detect,
        )

        # Filter issues to only changed files
        all_issues = results.get("issues", [])
        filtered_issues = [
            issue
            for issue in all_issues
            if any(issue.get("file", "").endswith(f) for f in python_files)
        ]

        # Update summary
        summary = results.get("summary", {}).copy()
        summary["total_issues"] = len(filtered_issues)
        summary["critical"] = sum(1 for i in filtered_issues if i.get("severity") == "critical")
        summary["high"] = sum(1 for i in filtered_issues if i.get("severity") == "high")
        summary["medium"] = sum(1 for i in filtered_issues if i.get("severity") == "medium")
        summary["low"] = sum(1 for i in filtered_issues if i.get("severity") == "low")

        results["summary"] = summary
        results["issues"] = filtered_issues

        # Display results
        total_issues = summary.get("total_issues", 0)

        if output == "summary":
            click.echo("=" * 60)
            click.echo("📊 Code Check Results")
            click.echo("=" * 60)
            click.echo(f"Total Issues: {total_issues}")
            click.echo(f"  Critical: {summary.get('critical', 0)}")
            click.echo(f"  High: {summary.get('high', 0)}")
            click.echo(f"  Medium: {summary.get('medium', 0)}")
            click.echo(f"  Low: {summary.get('low', 0)}")

            if filtered_issues:
                click.echo("\n⚠️  Issues in Changed Files:")
                for issue in filtered_issues[:20]:  # Show top 20
                    severity = issue.get("severity", "low").upper()
                    file = issue.get("file", "unknown")
                    line = issue.get("line", "?")
                    message = issue.get("message", "Unknown")
                    click.echo(f"   [{severity}] {file}:{line} - {message}")

            click.echo("=" * 60)
        else:
            click.echo(json.dumps(results, indent=2, default=str))

        if total_issues > 0:
            if fail_on_issues:
                click.echo(f"\n❌ Found {total_issues} issue(s) in changed files", err=True)
                sys.exit(1)
            else:
                click.echo(f"\n⚠️  Found {total_issues} issue(s) in changed files")
        else:
            click.echo("\n✅ No issues found in changed files!")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Git error: {e.stderr}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ Error: Git not found. Please install git.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def list_runs():
    """List all evaluation runs."""
    artifact_manager = ArtifactManager()

    runs = artifact_manager.list_runs()

    if not runs:
        click.echo("No evaluation runs found.")
        return

    click.echo(f"Found {len(runs)} evaluation run(s):\n")

    for run in runs:
        click.echo(f"Run ID: {run['run_id']}")
        click.echo(f"  Timestamp: {run.get('timestamp', 'unknown')}")
        click.echo(f"  Score: {run.get('overall_score', 0.0):.2f}/1.0")
        click.echo(f"  Behaviors: {', '.join(run.get('behaviors', []))}")
        click.echo()


@main.group()
def acp():
    """ACP (Agent Client Protocol) integration commands."""


@acp.command()
def register():
    """Register CodeOptiX as an ACP agent (for use with editors like Zed, JetBrains, Neovim)."""
    click.echo("🚀 Starting CodeOptiX as ACP agent...")
    click.echo("📝 CodeOptiX will be available to ACP-compatible editors")
    click.echo("💡 Connect from your editor using ACP protocol")
    click.echo()

    # Create CodeOptiX agent
    agent = CodeOptiXAgent()

    # Run agent (this blocks and handles ACP protocol)
    try:
        asyncio.run(run_agent(agent))
    except KeyboardInterrupt:
        click.echo("\n👋 CodeOptiX ACP agent stopped")


@acp.command()
@click.option("--agent-command", help="Command to spawn ACP agent (e.g., 'python agent.py')")
@click.option("--agent-name", help="Name of agent in registry (alternative to agent-command)")
@click.option(
    "--auto-eval/--no-auto-eval", default=True, help="Automatically evaluate code quality"
)
@click.option("--cwd", help="Working directory for the agent")
@click.option("--behaviors", help="Comma-separated behavior names to evaluate")
def bridge(
    agent_command: str | None,
    agent_name: str | None,
    auto_eval: bool,
    cwd: str | None,
    behaviors: str | None,
):
    """Use CodeOptiX as a quality bridge between editor and agent via ACP."""
    if not agent_command and not agent_name:
        click.echo("❌ Error: Either --agent-command or --agent-name must be provided", err=True)
        raise click.Abort()

    click.echo("🌉 Starting CodeOptiX ACP Quality Bridge...")
    if agent_command:
        click.echo(f"🤖 Agent command: {agent_command}")
    if agent_name:
        click.echo(f"🤖 Agent name: {agent_name}")
    click.echo(f"🔍 Auto-evaluation: {auto_eval}")
    click.echo()

    # Parse behaviors
    behavior_list = behaviors.split(",") if behaviors else None

    # Create evaluation engine if auto_eval
    evaluation_engine = None
    llm_client = None
    if auto_eval:
        from codeoptix.adapters.factory import create_adapter
        from codeoptix.evaluation import EvaluationEngine
        from codeoptix.utils.llm import LLMProvider, create_llm_client

        # Create a dummy adapter for evaluation
        adapter = create_adapter("claude-code", {})
        llm_client = create_llm_client(LLMProvider.OPENAI)
        evaluation_engine = EvaluationEngine(adapter, llm_client)

    # Create registry if using agent_name
    registry = None
    if agent_name:
        registry = ACPAgentRegistry()
        # Agent should be pre-registered, but we'll handle it

    # Parse agent command if provided
    agent_cmd = agent_command.split() if agent_command else None

    # Create quality bridge
    bridge = ACPQualityBridge(
        agent_command=agent_cmd,
        agent_name=agent_name,
        evaluation_engine=evaluation_engine,
        llm_client=llm_client,
        auto_eval=auto_eval,
        registry=registry,
        behaviors=behavior_list,
    )

    async def run_bridge():
        await bridge.connect(cwd=cwd)
        click.echo("✅ Quality bridge connected!")
        click.echo("💡 CodeOptiX will now evaluate all agent interactions")
        # Keep bridge running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            click.echo("\n👋 Quality bridge stopped")
            await bridge.close()

    try:
        asyncio.run(run_bridge())
    except KeyboardInterrupt:
        click.echo("\n👋 CodeOptiX quality bridge stopped")


@acp.command()
@click.option("--agent-command", help="Command to spawn ACP agent")
@click.option("--agent-name", help="Name of agent in registry")
@click.option("--prompt", required=True, help="Prompt to send to agent")
@click.option("--cwd", help="Working directory")
def connect(agent_command: str | None, agent_name: str | None, prompt: str, cwd: str | None):
    """Connect to an ACP agent and send a prompt."""
    if not agent_command and not agent_name:
        click.echo("❌ Error: Either --agent-command or --agent-name must be provided", err=True)
        raise click.Abort()

    if agent_command:
        click.echo(f"🔌 Connecting to ACP agent: {agent_command}")
    if agent_name:
        click.echo(f"🔌 Connecting to ACP agent: {agent_name}")

    # Parse agent command if provided
    agent_cmd = agent_command.split() if agent_command else None

    # Create registry if using agent_name
    registry = None
    if agent_name:
        registry = ACPAgentRegistry()

    # Create bridge and send prompt
    bridge = ACPQualityBridge(
        agent_command=agent_cmd,
        agent_name=agent_name,
        auto_eval=True,
        registry=registry,
    )

    async def run_connect():
        await bridge.connect(cwd=cwd)
        click.echo("✅ Connected!")
        click.echo(f"📤 Sending prompt: {prompt[:50]}...")
        result = await bridge.prompt(prompt)
        click.echo(f"✅ Response: {result}")
        await bridge.close()

    try:
        asyncio.run(run_connect())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@acp.group()
def registry():
    """Manage ACP agent registry."""


@registry.command("list")
def registry_list():
    """List all registered ACP agents."""
    registry = ACPAgentRegistry()
    agents = registry.list_agents()

    if not agents:
        click.echo("No agents registered.")
        return

    click.echo(f"Registered ACP agents ({len(agents)}):\n")
    for agent_name in agents:
        config = registry.get_agent(agent_name)
        click.echo(f"  • {agent_name}")
        if config and config.description:
            click.echo(f"    {config.description}")
        if config and config.command:
            click.echo(f"    Command: {' '.join(config.command)}")


@registry.command("add")
@click.option("--name", required=True, help="Agent name")
@click.option("--command", required=True, help="Command to spawn agent (e.g., 'python agent.py')")
@click.option("--cwd", help="Working directory")
@click.option("--description", help="Agent description")
def registry_add(name: str, command: str, cwd: str | None, description: str | None):
    """Register a new ACP agent."""
    registry = ACPAgentRegistry()
    registry.register(
        name=name,
        command=command.split(),
        cwd=cwd,
        description=description or "",
    )
    click.echo(f"✅ Registered agent: {name}")


@registry.command("remove")
@click.option("--name", required=True, help="Agent name")
def registry_remove(name: str):
    """Unregister an ACP agent."""
    registry = ACPAgentRegistry()
    registry.unregister(name)
    click.echo(f"✅ Unregistered agent: {name}")


@acp.command()
@click.option("--generate-agent", required=True, help="Agent name for code generation")
@click.option("--judge-agent", required=True, help="Agent name for code judgment")
@click.option("--prompt", required=True, help="Prompt for code generation")
def judge(generate_agent: str, judge_agent: str, prompt: str):
    """Use multi-agent judge: generate with one agent, judge with another."""
    click.echo("⚖️  Starting Multi-Agent Judge...")
    click.echo(f"🤖 Generate agent: {generate_agent}")
    click.echo(f"⚖️  Judge agent: {judge_agent}")
    click.echo()

    # Create registry
    registry = ACPAgentRegistry()

    # Create evaluation engine
    from codeoptix.adapters.factory import create_adapter
    from codeoptix.evaluation import EvaluationEngine
    from codeoptix.utils.llm import LLMProvider, create_llm_client

    adapter = create_adapter("claude-code", {})
    llm_client = create_llm_client(LLMProvider.OPENAI)
    evaluation_engine = EvaluationEngine(adapter, llm_client)

    # Create multi-agent judge
    judge = MultiAgentJudge(
        registry=registry,
        generate_agent=generate_agent,
        judge_agent=judge_agent,
        evaluation_engine=evaluation_engine,
        llm_client=llm_client,
    )

    async def run_judge():
        result = await judge.generate_and_judge(prompt)
        click.echo("✅ Multi-agent judge complete!")
        click.echo(f"\n📝 Generated Code:\n{result.get('generated_code', 'N/A')}")
        click.echo(f"\n⚖️  Judgment:\n{result.get('judgment', 'N/A')}")
        if result.get("evaluation_results"):
            click.echo(f"\n🔍 Evaluation Results:\n{result['evaluation_results']}")

    try:
        asyncio.run(run_judge())
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
