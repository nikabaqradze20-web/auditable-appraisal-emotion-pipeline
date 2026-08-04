# Traceability walkthrough

This walkthrough uses `SEG_SYN_001`, the canonical synthetic example. It is
chosen to show scope grouping, exclusion of third-party reports, derived anger,
benefactor gratitude, and a merged emotion profile.

## Input

```text
Question: How has the housing situation been, and has anything helped?
Answer:   The office cancelled our flat two weeks after they promised it.
          They had no right to do that, and we are still in the shelter.
          My neighbour says the same thing happened to her. A woman from
          the language school sits with me every Thursday and fills in the
          forms, otherwise I would not manage.
```

## Pass A: evidence and scope lock

Pass A extracts these evidence spans:

| Ref | Span | Scope |
| --- | --- | --- |
| `e1` | `The office cancelled our flat two weeks after they promised it` | `s1` |
| `e2` | `They had no right to do that` | `s1` |
| `e3` | `we are still in the shelter` | `s1` |
| `e4` | `A woman from the language school sits with me every Thursday and fills in the forms` | `s2` |
| `e5` | `otherwise I would not manage` | `s2` |

The sentence `My neighbour says the same thing happened to her` is not
extracted. It reports another person's experience and does not express the
respondent's own stance.

Pass A groups `e1,e2,e3` into one housing-obstacle scope and `e4,e5` into one
benefactor scope. It does not split on punctuation or create a scope for the
third-party report.

## Pass B: appraisal coding

| Scope | Focus | Agency | Temporal | Coping | Ordinals |
| --- | --- | --- | --- | --- | --- |
| `s1` | `blocked_goal` | `other` | `past`, `present` | `low` | norm violation `2` |
| `s2` | `benefactor` | `other` | `present` | `high` | `0` |

## Layer 2: deterministic emotion mapping

Layer 2 reads only the Pass B codes:

```text
s1 -> blocked_goal -> frustration (intensity 3)
s1 -> norm violation >= 2 + other agency -> anger_indignation (3)
s2 -> benefactor -> gratitude (2)
```

The merged profile is:

```json
{
  "frustration": 3,
  "anger_indignation": 3,
  "gratitude": 2
}
```

`anger_indignation` is additive and gate-derived. It is not a direct mapping
from the `blocked_goal` focus.

## Merged Layer 2 profile

Layer 2 scores each appraisal scope independently, then merges active labels by
union and keeps the maximum intensity per label:

```json
{
  "segment_emotions": {
    "frustration": 3,
    "anger_indignation": 3,
    "gratitude": 2
  }
}
```

An empty scope list produces `{}`. No separate segment-review layer is used in
this version; segment-level aggregation ends with the deterministic Layer 2
profile.

## Why this example matters

1. It contains no explicit emotion words.
2. It demonstrates a derived emotion gate.
3. It shows that a relevant third-party sentence can remain uncoded.
4. It shows two genuine appraisal situations rather than one scope per sentence.

The committed machine-readable result is
[`examples/SEG_SYN_001_trace.json`](../examples/SEG_SYN_001_trace.json). A test
re-runs the pipeline and compares the result with this file.

