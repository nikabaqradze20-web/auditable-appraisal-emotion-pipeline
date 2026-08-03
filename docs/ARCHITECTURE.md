# Architecture and extension guide

## Data flow

```text
question + answer
        |
        v
Layer 1: exact evidence + ordered locked scopes
        |  audit: quote and assignment integrity
        v
Layer 1.1: appraisal polarity, focus, criterion, support
        |  audit: immutable scope identity
        v
Layer 2: emotion, intensity, confidence, evidence refs
        |  audit: allowed mapping and support integrity
        v
Layer 3: complete segment review and final emotion aggregation
        |  audit: text preservation and review clarity
        v
traceable segment result
```

## Stable contracts

- `segment_id`, question, and answer are input identity.
- Evidence quotes must be exact substrings of the respondent answer.
- Evidence IDs are assigned once in Layer 1.
- Scope IDs are assigned once in Layer 1 and are immutable afterward.
- Later layers may add annotations but may not create, reorder, merge, or split scopes.
- Every appraisal and emotion must carry support references.
- Empty evidence is valid when the answer contains no supported appraisal.

## Current implementation

`src/emotion_pipeline/layers.py` contains transparent keyword rules so the
workflow runs without an API key. `src/emotion_pipeline/audits.py` implements
the safety boundary. `run_demo.py` is the public entry point.

## Model-backed extension

A future adapter can call an LLM at each layer, but it should:

1. keep the prompts in `prompts/` versioned;
2. require structured JSON matching `schemas/`;
3. validate each response before passing it forward;
4. store prompt/model/version metadata outside the text annotations;
5. never send raw personal data without an approved privacy and retention process.

Before claiming research validity, add independently coded gold-standard data,
an adjudication protocol, inter-annotator agreement, error analysis, and tests
for negation, ambiguity, mixed emotions, and long multi-scope answers.

