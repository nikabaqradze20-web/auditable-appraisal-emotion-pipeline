# Scope-first appraisal annotation pipeline

This repository is a public-safe, offline prototype for a two-pass LLM
annotation workflow. It currently implements **Pass A** and **Pass B** only.

The design is deliberately scope-first: every appraisal is attached to an
exact evidence quote and an immutable native scope. Future emotion scoring will
read these validated appraisals instead of reinterpreting the raw answer.

## Current status

```text
Implemented
  Pass A       evidence extraction + scope lock
  Pass B       appraisal annotation on locked scopes
  Layer 2     deterministic emotion scoring draft
  Layer 3     segment review and valence aggregation draft

Planned
  Validation  human-coded gold set and error analysis
```

This is a `v0.1-alpha` research prototype. It does not yet claim emotion
classification, psychological measurement, or production reliability.

## Why the two-pass design matters

Flat annotation often lets a later emotion label change the interpretation of
the text. This design creates a checkpoint first:

```text
respondent answer
      |
      v
Pass A: exact evidence + native scopes
      |
      v
Pass B: appraisal focus and polarity
      |
      v
future Layer 2: emotions
```

Pass B must preserve the scope IDs and evidence references created by Pass A.
Layer 2 then maps each validated appraisal to provisional emotions without
re-reading the evidence text. Layer 3 reviews the complete question-answer unit
and returns positive, negative, mixed, or neutral valence. Validators stop
invalid or unsupported outputs before they can flow forward.

## Traceability example

Synthetic segment `SEG_SYN_001` contains two scopes with opposite polarity:

```text
Question: What happened after you submitted the request?
Answer:   I was worried about the delay. Then the team replied, and I felt relieved.

e1 -> s1 -> negative / threat           -> anxiety_fear
e2 -> s2 -> positive / felt_alleviation -> relief_safety
```

The complete working trace is in
[`examples/SEG_SYN_001_trace.json`](examples/SEG_SYN_001_trace.json). The
step-by-step explanation is in [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).

For a mixed segment, Layer 3 can return:

```json
{
  "valence": "mixed",
  "emotion_present": "yes",
  "final_emotions": ["frustration", "hope"]
}
```

For a factual neutral answer, it returns `valence: neutral`,
`emotion_present: no`, and an empty emotion list. It does not invent a neutral
emotion label.

## Run it

Requires Python 3.10 or newer. The demo uses only the standard library:

```text
python run_demo.py
python -m unittest discover -s tests -v
```

The demo processes five synthetic segments, writes `demo_output.json`, and
reports Pass A, Pass B, and draft Layer 2 audit results. The output file is
ignored by Git.

## Repository map

- `data/` - synthetic question-answer fixtures only.
- `prompts/` - provider-neutral Pass A, Pass B, and draft Layer 2 contracts.
- `schemas/` - input and output JSON contracts.
- `src/emotion_pipeline/` - deterministic reference implementation and audits.
- `examples/` - committed synthetic trace showing evidence continuity.
- `docs/` - architecture, traceability, manual draft, and roadmap notes.
- `tests/` - standard-library tests for the workflow.

## Privacy boundary

Do not add raw transcripts, exports, API responses, names, emails, locations,
or generated pilot workbooks. Real data must remain outside Git and outside the
synthetic fixtures. The local legacy pilot artifacts are ignored by
[`.gitignore`](.gitignore).

## Limitations and next work

The current demo uses transparent keyword rules to make the contracts runnable
without an API key. Layer 2 intensity modifiers, derived gates, and Layer 3
aggregation are provisional; the project is not a gold standard and has not
been validated on real interview material.

Before treating emotion scoring or segment valence as reliable, stabilize the
appraisal manual and create a human-coded gold set. Then validate the draft
Layer 2 gates and Layer 3 aggregation. See
[`docs/ANNOTATION_MANUAL_DRAFT.md`](docs/ANNOTATION_MANUAL_DRAFT.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

