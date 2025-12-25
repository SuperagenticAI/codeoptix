# GEPA Integration - Quick Summary

## TL;DR

- **When**: During prompt evolution (`EvolutionEngine.evolve()`)
- **Where**: `MinimalGEPAProposer.propose_improved_prompt()` in `src/codeoptix/evolution/gepa_integration.py`
- **What**: Uses GEPA's `InstructionProposalSignature` to propose improved prompts
- **Which LLM**: Same LLM client passed to `EvolutionEngine` (default: OpenAI GPT-4o)
- **How**: Converts evaluation failures → reflective dataset → GEPA format → LLM call → improved prompt

## Quick Answer

### When is GEPA used?
**During prompt evolution**, specifically when `EvolutionEngine.evolve()` is called.

### Where does GEPA do optimization?
**In `MinimalGEPAProposer.propose_improved_prompt()`**:
- Takes current prompt + evaluation failures
- Uses GEPA's `InstructionProposalSignature`
- Calls LLM to generate improved prompt

### Which LLM is used?
**The same LLM client passed to `EvolutionEngine`**:
```python
llm_client = create_llm_client(LLMProvider.OPENAI)  # ← This one
evolution_engine = EvolutionEngine(..., llm_client=llm_client)
# GEPA uses this same llm_client
```

### How is it demonstrated?
Run: `python examples/gepa_demonstration.py`

## Visual Flow

```
Evaluation Results (failures)
    ↓
Reflective Dataset
    ↓
GEPA Format Conversion
    ↓
GEPA's InstructionProposalSignature
    ↓
LLM Call (GPT-4o) ← GEPA uses this
    ↓
Improved Prompt
    ↓
Test on Minibatch
    ↓
Select Best Candidate
    ↓
Iterate
```

## Code Locations

1. **GEPA Integration**: `src/codeoptix/evolution/gepa_integration.py`
2. **Evolution Engine**: `src/codeoptix/evolution/engine.py`
3. **Prompt Proposer**: `src/codeoptix/evolution/proposer.py`
4. **Example**: `examples/gepa_demonstration.py`

## See Also

- [GEPA_DETAILED.md](GEPA_DETAILED.md) - Complete explanation
- [GEPA_INTEGRATION.md](advanced/gepa.md) - Integration overview
- `examples/gepa_demonstration.py` - Working example

