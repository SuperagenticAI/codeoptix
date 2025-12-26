#!/usr/bin/env python3
"""
Quick Start: Single Behavior Example
Perfect for open-source users getting started with CodeOptiX

This example demonstrates how to use CodeOptiX with a single behavior.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from codeoptix.adapters.factory import create_adapter
from codeoptix.evaluation import EvaluationEngine
from codeoptix.utils.llm import LLMProvider, create_llm_client


def main():
    """Run a simple evaluation with a single behavior."""

    print("=" * 60)
    print("CodeOptiX Quick Start: Single Behavior")
    print("=" * 60)
    print()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print()
        print("Please set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print()
        print("Or use a different provider:")
        print("  export ANTHROPIC_API_KEY='your-key-here'  # For Claude Code")
        print("  export GOOGLE_API_KEY='your-key-here'    # For Gemini")
        sys.exit(1)

    # Configuration for single behavior
    print("📋 Configuration:")
    print("   Agent: claude-code")
    print("   Behavior: insecure-code (security checks)")
    print("   LLM Provider: openai")
    print()

    try:
        # Create adapter
        print("🔧 Setting up adapter...")
        adapter_config = {
            "llm_config": {
                "provider": "anthropic",
                "model": "claude-opus-4-5-20251101",
                "api_key": os.getenv("ANTHROPIC_API_KEY") or api_key,
            }
        }

        adapter = create_adapter("claude-code", adapter_config)
        print(f"   ✅ Adapter created: {adapter.get_adapter_type()}")

        # Create LLM client
        print("🔧 Setting up LLM client...")
        llm_client = create_llm_client(LLMProvider.OPENAI, api_key=api_key)
        print("   ✅ LLM client ready")

        # Create evaluation engine with minimal config
        print("🔧 Setting up evaluation engine...")
        eval_config = {
            "scenario_generator": {
                "num_scenarios": 2,  # Small number for quick start
                "use_bloom": False,  # Disable Bloom for simplicity
            }
        }
        eval_engine = EvaluationEngine(adapter, llm_client, config=eval_config)
        print("   ✅ Evaluation engine ready")

        # Run evaluation with single behavior
        print()
        print("🚀 Running evaluation...")
        print("   This may take a minute...")
        print()

        results = eval_engine.evaluate_behaviors(
            behavior_names=["insecure-code"],
            context={"plan": "Create a simple authentication function"},
        )

        # Display results
        print("=" * 60)
        print("✅ Evaluation Complete!")
        print("=" * 60)

        overall_score = results.get("overall_score", 0.0)
        print(f"📊 Overall Score: {overall_score:.2%}")
        print()

        behaviors = results.get("behaviors", {})
        if "insecure-code" in behaviors:
            behavior_data = behaviors["insecure-code"]
            passed = behavior_data.get("passed", True)
            score = behavior_data.get("score", 0.0)
            emoji = "✅" if passed else "❌"

            print(f"{emoji} insecure-code: {score:.2%}")

            if not passed and behavior_data.get("evidence"):
                print()
                print("⚠️  Issues found:")
                for evidence in behavior_data["evidence"][:3]:
                    print(f"   - {evidence}")

        print()
        print("=" * 60)
        print("💡 Next Steps:")
        print("=" * 60)
        print("1. Try other behaviors:")
        print("   - vacuous-tests (test quality)")
        print("   - plan-drift (requirements alignment)")
        print()
        print("2. Use the CLI:")
        print("   codeoptix eval --agent claude-code --behaviors insecure-code")
        print()
        print("3. Use a config file:")
        print("   codeoptix eval --agent claude-code --behaviors insecure-code \\")
        print("     --config examples/configs/single-behavior-insecure-code.yaml")
        print()
        print("4. Check the documentation:")
        print("   https://codeoptix.ai/docs")
        print()

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("💡 Tips:")
        print("   - Check your API key is correct")
        print("   - Verify the agent type is supported")
        print("   - Ensure the behavior name is correct")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   - Check your API key has sufficient credits")
        print("   - Verify your internet connection")
        print("   - Try again in a few moments")
        if hasattr(e, "__cause__") and e.__cause__:
            print(f"   - Details: {e.__cause__}")
        sys.exit(1)


if __name__ == "__main__":
    main()
