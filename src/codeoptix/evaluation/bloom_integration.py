"""Full Bloom integration for scenario generation."""

import json
from typing import Any

from codeoptix.utils.llm import LLMClient
from codeoptix.vendor.bloom.prompts.step2_ideation import (
    make_all_scenarios_prompt,
    make_system_prompt,
    make_variation_prompt,
    make_variation_system_prompt,
)


class BloomIdeationIntegration:
    """
    Full Bloom ideation integration for scenario generation.

    Uses vendored Bloom scripts for sophisticated scenario ideation
    and variation generation.
    """

    def __init__(self, llm_client: LLMClient, config: dict[str, Any] | None = None):
        """
        Initialize Bloom ideation integration.

        Args:
            llm_client: LLM client for scenario generation
            config: Configuration dictionary
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.model = self.config.get("model", "gpt-4o")
        self.num_base_scenarios = self.config.get("num_base_scenarios", 3)
        self.num_variations = self.config.get("num_variations", 2)

    def generate_scenarios(
        self,
        behavior_name: str,
        behavior_description: str,
        examples: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate scenarios using full Bloom ideation pipeline.

        Args:
            behavior_name: Name of the behavior
            behavior_description: Description of the behavior
            examples: Optional example scenarios

        Returns:
            List of scenario dictionaries
        """
        # Step 1: Generate base scenarios using Bloom ideation
        base_scenarios = self._generate_base_scenarios(
            behavior_name=behavior_name,
            behavior_description=behavior_description,
            examples=examples or [],
        )

        # Step 2: Generate variations for each base scenario
        all_scenarios = []
        for base_scenario in base_scenarios:
            all_scenarios.append(base_scenario)

            # Generate variations
            variations = self._generate_variations(
                base_scenario=base_scenario,
                behavior_name=behavior_name,
                behavior_description=behavior_description,
            )
            all_scenarios.extend(variations)

        return all_scenarios[: self.num_base_scenarios * (1 + self.num_variations)]

    def _generate_base_scenarios(
        self, behavior_name: str, behavior_description: str, examples: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate base scenarios using Bloom ideation prompts."""
        # Create system prompt using Bloom's ideation system prompt
        system_prompt = make_system_prompt(
            behavior_name=behavior_name, behavior_description=behavior_description
        )

        # Create scenarios prompt
        scenarios_prompt = make_all_scenarios_prompt(
            behavior_name=behavior_name,
            behavior_description=behavior_description,
            total_scenarios=self.num_base_scenarios,
            examples=examples,
        )

        # Use LLM client to generate scenarios
        try:
            # Convert to litellm format for Bloom compatibility
            response = self._call_llm_with_bloom_format(
                system_prompt=system_prompt, user_prompt=scenarios_prompt
            )

            # Parse scenarios from response
            scenarios = self._parse_scenarios_from_response(response, behavior_name)
            return scenarios[: self.num_base_scenarios]
        except Exception:
            # Fallback to simple scenarios on error
            return self._fallback_scenarios(behavior_name, behavior_description)

    def _generate_variations(
        self, base_scenario: dict[str, Any], behavior_name: str, behavior_description: str
    ) -> list[dict[str, Any]]:
        """Generate variations of a base scenario using Bloom variation prompts."""
        variations = []

        # Create variation system prompt
        variation_system_prompt = make_variation_system_prompt(
            behavior_name=behavior_name, behavior_description=behavior_description
        )

        # Create variation prompt
        variation_prompt = make_variation_prompt(
            base_scenario_description=base_scenario.get("prompt", ""),
            num_perturbations=self.num_variations + 1,  # +1 because Bloom counts differently
        )

        try:
            response = self._call_llm_with_bloom_format(
                system_prompt=variation_system_prompt, user_prompt=variation_prompt
            )

            # Parse variations from response
            parsed_variations = self._parse_variations_from_response(
                response, base_scenario, behavior_name
            )
            variations.extend(parsed_variations[: self.num_variations])
        except Exception:
            # If variation generation fails, just return the base scenario
            pass

        return variations

    def _call_llm_with_bloom_format(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call LLM using Bloom's expected format (litellm-compatible).

        This bridges CodeOptix's LLM client with Bloom's expected interface.
        """
        # Use CodeOptix's LLM client, but format for Bloom compatibility
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return self.llm_client.chat_completion(
            messages=messages,
            model=self.model,
            temperature=0.8,  # Higher temperature for creative generation
        )

    def _parse_scenarios_from_response(
        self, response: str, behavior_name: str
    ) -> list[dict[str, Any]]:
        """Parse scenarios from LLM response."""
        scenarios = []

        # Try to extract JSON from response
        try:
            # Look for JSON array
            import re

            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                scenarios = json.loads(json_match.group(0))
                return [self._normalize_scenario(s, behavior_name) for s in scenarios]
        except json.JSONDecodeError:
            pass

        # Fallback: try to parse structured text
        # Look for scenario markers
        scenario_pattern = r"<scenario>|Scenario \d+:|## Scenario"
        if re.search(scenario_pattern, response, re.IGNORECASE):
            # Parse structured scenarios
            parts = re.split(scenario_pattern, response, flags=re.IGNORECASE)
            for part in parts[1:]:  # Skip first part (before first scenario)
                scenario = self._extract_scenario_from_text(part, behavior_name)
                if scenario:
                    scenarios.append(scenario)

        return scenarios if scenarios else self._fallback_scenarios(behavior_name, "")

    def _parse_variations_from_response(
        self, response: str, base_scenario: dict[str, Any], behavior_name: str
    ) -> list[dict[str, Any]]:
        """Parse variations from LLM response."""
        variations = []

        # Look for variation markers
        import re

        variation_pattern = r"<variation>|Variation \d+:|## Variation"
        if re.search(variation_pattern, response, re.IGNORECASE):
            parts = re.split(variation_pattern, response, flags=re.IGNORECASE)
            for part in parts[1:]:  # Skip first part
                variation = base_scenario.copy()
                variation["prompt"] = part.strip()[:500]  # Limit length
                variation["task"] = f"Variation: {base_scenario.get('task', '')}"
                variations.append(variation)

        return variations

    def _normalize_scenario(self, scenario: Any, behavior_name: str) -> dict[str, Any]:
        """Normalize scenario to standard format."""
        if isinstance(scenario, dict):
            return {
                "task": scenario.get("task", scenario.get("description", "")),
                "prompt": scenario.get("prompt", scenario.get("instruction", "")),
                "expected_issues": scenario.get("expected_issues", []),
                "behavior": behavior_name,
            }
        if isinstance(scenario, str):
            return {
                "task": f"Test {behavior_name}",
                "prompt": scenario,
                "expected_issues": [],
                "behavior": behavior_name,
            }
        return {
            "task": f"Test {behavior_name}",
            "prompt": str(scenario),
            "expected_issues": [],
            "behavior": behavior_name,
        }

    def _extract_scenario_from_text(self, text: str, behavior_name: str) -> dict[str, Any] | None:
        """Extract scenario information from text."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return None

        # Try to extract task and prompt
        task = ""
        prompt = ""

        for i, line in enumerate(lines):
            if "task:" in line.lower() or "description:" in line.lower():
                task = line.split(":", 1)[1].strip() if ":" in line else line
            elif "prompt:" in line.lower() or "instruction:" in line.lower():
                prompt = line.split(":", 1)[1].strip() if ":" in line else line
            elif i == 0 and not task:
                task = line

        if not prompt:
            prompt = "\n".join(lines)

        return {
            "task": task or f"Test {behavior_name}",
            "prompt": prompt[:500],  # Limit length
            "expected_issues": [],
            "behavior": behavior_name,
        }

    def _fallback_scenarios(
        self, behavior_name: str, behavior_description: str
    ) -> list[dict[str, Any]]:
        """Generate fallback scenarios if Bloom generation fails."""
        return [
            {
                "task": f"Test {behavior_name}",
                "prompt": f"Write code that should be evaluated for: {behavior_description}",
                "expected_issues": [f"Behavior: {behavior_name}"],
                "behavior": behavior_name,
            }
        ]
