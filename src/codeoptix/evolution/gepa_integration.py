"""Minimal GEPA integration for CodeOptiX evolution.

This module provides a minimal integration with GEPA (Genetic-Pareto) by using
GEPA's InstructionProposalSignature component for prompt evolution.

Note: This is NOT a full GEPA framework integration. We're using GEPA's proven
instruction proposal mechanism rather than the complete GEPA optimization engine.
"""

from typing import Any

from gepa.strategies.instruction_proposal import InstructionProposalSignature


class MinimalGEPAProposer:
    """
    Minimal GEPA integration for prompt proposal.

    Uses GEPA's InstructionProposalSignature for prompt evolution.
    """

    def __init__(self, llm_client, config: dict[str, Any] | None = None):
        """
        Initialize minimal GEPA proposer.

        Args:
            llm_client: LLM client compatible with GEPA's LanguageModel interface
            config: Configuration dictionary
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.prompt_template = self.config.get(
            "prompt_template", InstructionProposalSignature.default_prompt_template
        )

    def propose_improved_prompt(
        self,
        current_prompt: str,
        reflective_dataset: list[dict[str, Any]],
        component_name: str = "system_prompt",
    ) -> str:
        """
        Propose improved prompt using GEPA's InstructionProposalSignature.

        Args:
            current_prompt: Current prompt text
            reflective_dataset: List of failure examples with feedback
            component_name: Name of the component

        Returns:
            Proposed improved prompt text
        """
        # Convert reflective dataset to GEPA format
        gepa_dataset = self._convert_to_gepa_format(reflective_dataset)

        # Use GEPA's instruction proposal
        result = InstructionProposalSignature.run(
            lm=self._wrap_llm_client(),
            input_dict={
                "current_instruction_doc": current_prompt,
                "dataset_with_feedback": gepa_dataset,
                "prompt_template": self.prompt_template,
            },
        )

        return result["new_instruction"]

    def _convert_to_gepa_format(
        self, reflective_dataset: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Convert CodeOptiX reflective dataset to GEPA format.

        GEPA's InstructionProposalSignature expects a dataset with this structure:
        {
            "Inputs": Dict[str, str],           # Task inputs
            "Generated Outputs": Dict[str, str] | str,  # Model outputs
            "Feedback": str                     # Feedback on performance
        }

        This format is used by GEPA's default prompt template to generate
        improved instructions through reflective mutation.
        """
        gepa_format = []

        for example in reflective_dataset:
            gepa_example = {
                "Inputs": {
                    "task": example.get("scenario", ""),
                    "behavior": example.get("behavior", ""),
                },
                "Generated Outputs": {
                    "score": example.get("score", 0.0),
                    "evidence": example.get("evidence", []),
                },
                "Feedback": self._generate_feedback(example),
            }
            gepa_format.append(gepa_example)

        return gepa_format

    def _generate_feedback(self, example: dict[str, Any]) -> str:
        """Generate feedback string from example."""
        behavior = example.get("behavior", "unknown")
        score = example.get("score", 0.0)
        evidence = example.get("evidence", [])

        feedback = f"Behavior '{behavior}' scored {score:.2f}/1.0. "

        if evidence:
            feedback += "Issues found: " + "; ".join(evidence[:3])
        else:
            feedback += "No specific issues identified."

        return feedback

    def _wrap_llm_client(self):
        """
        Wrap CodeOptiX LLM client to GEPA's LanguageModel interface.

        GEPA expects a LanguageModel Protocol with a __call__ method that takes
        a prompt string and returns a string response.
        """

        class GEPALLMWrapper:
            def __init__(self, llm_client):
                self.llm_client = llm_client
                # Get default model from config if available
                self.default_model = "gpt-4o"  # Default fallback
                if hasattr(llm_client, "config") and isinstance(llm_client.config, dict):
                    self.default_model = llm_client.config.get("model", self.default_model)

            def __call__(self, prompt: str) -> str:
                """
                Generate response using CodeOptiX LLM client.

                This implements GEPA's LanguageModel Protocol:
                - Takes a prompt string
                - Returns a string response
                """
                response = self.llm_client.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.default_model,
                    temperature=0.7,
                )
                # Ensure we return a string
                return str(response) if response else ""

        return GEPALLMWrapper(self.llm_client)
