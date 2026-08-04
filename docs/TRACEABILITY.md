# Two-pass traceability walkthrough

This document follows one synthetic segment through the implemented workflow.
Pass A and Pass B are the appraisal foundation. Layer 2 is a deterministic
working draft; Layer 3 segment aggregation is not implemented yet.

## Input unit

```text
segment_id: SEG_SYN_001
question:   What happened after you submitted the request?
answer:     I was worried about the delay. Then the team replied, and I felt relieved.
```

The question supplies context. Evidence comes from the respondent answer.

## Pass A: evidence and scope lock

Pass A extracts exact, contiguous quotes and creates native scopes in order:

| Evidence | Exact quote | Scope |
| --- | --- | --- |
| `e1` | `I was worried about the delay.` | `s1` |
| `e2` | `Then the team replied, and I felt relieved.` | `s2` |

The answer contains a negative worry and a later positive relief response, so
two scopes are justified. `s2` records its independent relation to `s1`.

## Pass B: appraisal annotation

Pass B keeps the scope IDs and attaches appraisal labels:

| Scope | Polarity | Focus | Criterion | Support |
| --- | --- | --- | --- | --- |
| `s1` | `negative` | `threat` | possible harm is salient | `e1` |
| `s2` | `positive` | `felt_alleviation` | acute burden described as ended | `e2` |

The trace is therefore:

```text
e1 -> s1 -> negative / threat
e2 -> s2 -> positive / felt_alleviation
```

## Layer 2 draft: deterministic emotion scoring

Layer 2 reads only the validated Pass B scopes. It produces:

| Scope | Core emotion | Intensity |
| --- | --- | --- |
| `s1` / `threat` | `anxiety_fear` | `3` |
| `s2` / `felt_alleviation` | `relief_safety` | `2` |

The merged segment profile is:

```json
{"anxiety_fear": 3, "relief_safety": 2}
```

The result is provisional. The intensity formula and derived gates must be
tested against a human-coded gold set.

## Audit gates

The current implementation records three audits:

1. Pass A checks exact quotes, unique evidence IDs, and complete evidence assignment.
2. Pass B checks immutable scope identity, allowed focus labels, and support references.
3. Layer 2 checks immutable scope identity, scoring errors, and intensity bounds.

The machine-readable result is
[`examples/SEG_SYN_001_trace.json`](../examples/SEG_SYN_001_trace.json). A test
re-runs the pipeline and compares it with this committed trace.

## Layer 3 draft: segment review

Layer 3 reviews the full question-answer segment and uses the merged Layer 2
profile:

```json
{
  "valence": "mixed",
  "emotion_present": "yes",
  "final_emotions": ["anxiety_fear", "relief_safety"]
}
```

When Layer 2 returns no emotions, Layer 3 returns `valence: neutral`,
`emotion_present: no`, and `final_emotions: []`. Layer 3 is still a draft and
needs validation against human-coded examples.

