# Auditable appraisal -> emotion pipeline

This repository is a small, public-safe reference implementation of a four-layer annotation workflow for one moderator question plus one respondent answer.

The project is intentionally offline and deterministic. It demonstrates the contracts, evidence flow, and audits that a later model-backed implementation can follow. The examples are synthetic and contain no real interview records or personal names.

## Workflow

1. **Layer 1 - appraisal extraction and scope lock**: extract exact evidence and create ordered independent scopes.
2. **Layer 1.1 - appraisal-scheme annotation**: classify each locked scope using an explicit appraisal focus and evidence references.
3. **Layer 2 - emotion annotation**: map validated appraisals to emotions, intensity, confidence, and evidence.
4. **Layer 3 - segment construction and final review**: inspect the complete question-answer unit and produce final segment-level emotions.

Every layer emits an audit. A pipeline run stops if a scope identity changes, a quote is not exact, a label is outside the contract, or evidence is missing.

## Run it

Requires Python 3.10 or newer and no external packages:

```text
python run_demo.py
python -m unittest discover -s tests -v
```

The demo writes `demo_output.json`, which is ignored by Git.

## Traceability example

`SEG_SYN_001` demonstrates two scopes with opposite polarity:

```text
Question: What happened after you submitted the request?
Answer:   I was worried about the delay. Then the team replied, and I felt relieved.

e1 -> s1 -> negative / threat           -> fear
e2 -> s2 -> positive / felt_alleviation -> relief
```

The final Layer 3 segment retains the original question and answer and returns
`final_emotions: ["fear", "relief"]`. The complete saved trace is in
[`examples/SEG_SYN_001_trace.json`](examples/SEG_SYN_001_trace.json), and the
step-by-step explanation is in [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).

The identity invariant is simple: Layer 1 creates `scope_id` values; Layers 1.1
and 2 must return the same IDs in the same order; Layer 3 may aggregate those
validated results but cannot create an unsupported evidence trail.

## Project layout

- `prompts/` â€” provider-neutral prompt contracts for all four layers.
- `schemas/` â€” JSON output shapes for each layer.
- `src/emotion_pipeline/` â€” deterministic reference implementation and audits.
- `data/synthetic_segments.json` â€” synthetic question-answer fixtures only.
- `examples/` â€” one committed, fully traceable synthetic pipeline result.
- `docs/` â€” architecture, traceability, privacy, and extension notes.
- `tests/` â€” contract and end-to-end tests.

## What this is and is not

This is a reviewable baseline for designing and testing an auditable annotation
workflow. It is not a validated psychological measurement instrument, a
production classifier, or a claim that the keyword rules generalize to real
interviews. The deterministic layer functions make the contracts executable;
future model-backed implementations must preserve those contracts and pass the
same audits.

## Privacy boundary

Do not add raw transcripts, exports, API responses, names, emails, locations, or generated pilot workbooks to this repository. Real data should be filtered before entering the pipeline and should remain outside Git. Legacy local pilot artifacts are ignored by `.gitignore` and are not part of the public implementation.

## Next step for a model-backed version

Replace the deterministic functions in `src/emotion_pipeline/layers.py` with model calls that return the same JSON contracts. Keep the audits and synthetic tests unchanged; they are the safety boundary between prompts and downstream analysis.

