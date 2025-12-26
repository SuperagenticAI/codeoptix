"""Prompt proposer using GEPA-style reflective mutation."""

from typing import Any

from codeoptix.evolution.gepa_integration import MinimalGEPAProposer
from codeoptix.utils.llm import LLMClient


class PromptProposer:
    """
    Proposes improved prompts using GEPA-style reflective mutation.

    Uses evaluation results and reflection to generate improved prompt variants.
    """

    def __init__(self, llm_client: LLMClient, config: dict[str, Any] | None = None):
        """
        Initialize prompt proposer.

        Args:
            llm_client: LLM client for generating proposals
            config: Configuration dictionary
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.use_gepa = self.config.get("use_gepa", True)  # Use GEPA by default

        # Initialize GEPA proposer if enabled
        if self.use_gepa:
            self.gepa_proposer = MinimalGEPAProposer(llm_client, config)
        else:
            self.gepa_proposer = None
            self.model = self.config.get("model", "gpt-4o")
            self.temperature = self.config.get("temperature", 0.7)

    def propose_improved_prompt(
        self,
        current_prompt: str,
        evaluation_results: dict[str, Any],
        reflection: str,
        component_name: str = "system_prompt",
    ) -> str:
        """
        Propose an improved prompt based on evaluation results and reflection.

        Args:
            current_prompt: Current prompt text
            evaluation_results: Evaluation results dictionary
            reflection: Reflection markdown content
            component_name: Name of the prompt component

        Returns:
            Proposed improved prompt text
        """
        # Build reflective dataset from evaluation results
        reflective_data = self._build_reflective_dataset(evaluation_results)

        # Use GEPA if enabled
        if self.use_gepa and self.gepa_proposer:
            return self.gepa_proposer.propose_improved_prompt(
                current_prompt=current_prompt,
                reflective_dataset=reflective_data,
                component_name=component_name,
            )

        # Fallback to custom implementation
        # Create proposal prompt
        proposal_prompt = self._create_proposal_prompt(
            current_prompt=current_prompt,
            reflective_data=reflective_data,
            reflection=reflection,
            component_name=component_name,
        )

        # Get proposal from LLM
        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": proposal_prompt}],
            model=self.model,
            temperature=self.temperature,
        )

        # Extract proposed prompt
        proposed_prompt = self._extract_proposed_prompt(response, current_prompt)

        return proposed_prompt

    def _build_reflective_dataset(self, evaluation_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Build reflective dataset from evaluation results."""
        dataset = []

        behaviors = evaluation_results.get("behaviors", {})

        for behavior_name, behavior_data in behaviors.items():
            score = behavior_data.get("score", 0.0)
            evidence = behavior_data.get("evidence", [])
            scenario_results = behavior_data.get("scenario_results", [])

            # Collect failure examples
            if score < 0.7:  # Focus on failures
                for scenario_result in scenario_results:
                    behavior_result = scenario_result.get("behavior_result", {})
                    if not behavior_result.get("passed", True):
                        dataset.append(
                            {
                                "behavior": behavior_name,
                                "score": score,
                                "evidence": evidence[:3],  # Limit evidence
                                "scenario": scenario_result.get("scenario", {}).get("prompt", ""),
                            }
                        )

        return dataset

    def _create_proposal_prompt(
        self,
        current_prompt: str,
        reflective_data: list[dict[str, Any]],
        reflection: str,
        component_name: str,
    ) -> str:
        """Create prompt for LLM to propose improved prompt."""

        # Format reflective data
        failure_examples = []
        for i, data in enumerate(reflective_data[:5], 1):  # Limit to 5 examples
            failure_examples.append(
                f"Example {i}:\n"
                f"  Behavior: {data['behavior']}\n"
                f"  Score: {data['score']:.2f}\n"
                f"  Issues: {', '.join(data['evidence'][:2])}\n"
            )

        prompt = f"""You are optimizing a coding agent's prompt to improve its behavior.

Current {component_name}:
```
{current_prompt}
```

Evaluation Results Summary:
{reflection[:1000]}...

Specific Failure Examples:
{"".join(failure_examples)}

Based on the evaluation results and reflection above, propose an improved version of the {component_name} that addresses the identified issues.

The improved prompt should:
1. Address the root causes identified in the reflection
2. Include specific guidance to prevent the failures observed
3. Maintain the original intent while adding necessary constraints
4. Be clear, actionable, and specific

Provide ONLY the improved prompt text, without additional explanation or markdown formatting.
"""

        return prompt

    def _extract_proposed_prompt(self, response: str, fallback: str) -> str:
        """Extract proposed prompt from LLM response."""
        # Try to extract code block
        import re

        # Look for code blocks
        code_blocks = re.findall(r"```(?:.*)?\n(.*?)```", response, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()

        # Look for text between markers
        if "Current" in response and "Improved" in response:
            # Try to extract after "Improved" marker
            improved_section = response.split("Improved")[-1]
            # Take first substantial paragraph
            lines = [l.strip() for l in improved_section.split("\n") if l.strip()]
            if lines:
                return "\n".join(lines[:10])  # Take first 10 non-empty lines

        # Fallback: use response as-is, but clean it up
        cleaned = response.strip()
        # Remove common prefixes
        for prefix in ["Improved prompt:", "Here's the improved prompt:", "Proposed prompt:"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()

        return cleaned if cleaned else fallback
