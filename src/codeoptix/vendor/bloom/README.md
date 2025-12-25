# Vendored Bloom Framework

This directory contains vendored code from the Bloom evaluation framework.

## Source

Bloom is an open-source tool for automated behavior evaluation of LLMs. Since it's not available on PyPI, we vendor the necessary components here.

## Files

- `utils.py` - Core utility functions for Bloom
- `globals.py` - Global configuration and model definitions
- `transcript_utils.py` - Transcript handling utilities
- `prompts/` - Prompt templates for evaluation stages
- `orchestrators/` - Orchestration logic for conversations and simulated environments
- `scripts/` - Evaluation stage scripts (ideation, judgment)
- `schemas/` - JSON schemas for behaviors and conversations

## Usage

The vendored Bloom code is used by CodeOptiX's evaluation engine for scenario generation and behavioral evaluation. It's accessed through the `codeoptix.vendor.bloom` namespace.

## Modifications

All imports have been updated to use the `codeoptix.vendor.bloom` namespace instead of relative imports.

