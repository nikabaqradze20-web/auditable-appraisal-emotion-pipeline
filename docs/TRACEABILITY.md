# Traceability walkthrough

This document follows one synthetic segment through every layer. The purpose is
to make the evidence chain inspectable by a reviewer.

## Input unit

The unit of analysis is one moderator question plus one respondent answer:

```text
segment_id: SEG_SYN_001
question:   What happened after you submitted the request?
answer:     I was worried about the delay. Then the team replied, and I felt relieved.
```

The moderator question provides context only. Appraisal evidence must come from
the respondent answer.

## Layer 1: extraction and scope lock

Layer 1 extracts exact contiguous quotes. It creates one scope for each
independent respondent stance and keeps scopes in evidence order.

| Evidence | Exact quote | Locked scope |
| --- | --- | --- |
| `e1` | `I was worried about the delay.` | `s1` |
| `e2` | `Then the team replied, and I felt relieved.` | `s2` |

`s2` records that it follows `s1` as an independent scope. The relation is
structural; it does not alter the text or merge the scopes.

```json
{
  "scopes": [
    {"scope_id": "s1", "stance_refs": ["e1"]},
    {"scope_id": "s2", "stance_refs": ["e2"], "relations_to_prior_scopes": [
      {"scope_id": "s1", "relation": "independent"}
    ]}
  ]
}
```

## Layer 1.1: appraisal scheme

The appraisal layer cannot create new scopes. It annotates the locked IDs:

| Scope | Polarity | Focus | Criterion | Support |
| --- | --- | --- | --- | --- |
| `s1` | `negative` | `threat` | possible harm is salient | `e1` |
| `s2` | `positive` | `felt_alleviation` | an acute burden is described as ended | `e2` |

The negative and positive appraisals remain separate because the answer
contains both an earlier worry and a later relief response.

## Layer 2: emotion annotation

Layer 2 maps each validated appraisal to an emotion while preserving the scope
and evidence references:

| Scope | Appraisal | Emotion | Intensity | Evidence |
| --- | --- | --- | --- | --- |
| `s1` | `threat` | `fear` | `high` | `e1` |
| `s2` | `felt_alleviation` | `relief` | `medium` | `e2` |

## Layer 3: segment construction and final review

The final reviewer sees the complete question-answer unit and the validated
emotion scopes. It preserves the input text and aggregates the distinct final
emotions:

```json
{
  "segment_id": "SEG_SYN_001",
  "final_emotions": ["fear", "relief"],
  "primary_emotion": "fear",
  "review": {
    "clear": true,
    "scope_count": 2
  }
}
```

`primary_emotion` is a demo aggregation rule, not a psychological truth claim.
A production study should define that rule with an annotation manual and human
review.

## Audit gates

The pipeline records four pass/fail audits:

1. Layer 1 checks exact quotes, unique evidence IDs, and complete evidence assignment.
2. Layer 1.1 checks immutable scope identity, allowed focus labels, and appraisal support.
3. Layer 2 checks immutable scope identity, allowed emotion mappings, and evidence references.
4. Layer 3 checks preserved question-answer text, segment identity, and review clarity.

The committed machine-readable result is
[`examples/SEG_SYN_001_trace.json`](../examples/SEG_SYN_001_trace.json). A test
re-runs the pipeline and compares it with that example so documentation cannot
drift silently from the implementation.

