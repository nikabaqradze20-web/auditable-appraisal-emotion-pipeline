# Traceability walkthrough

This walkthrough follows `SEG_SYN_001`, the canonical synthetic example, from
the answer to the emotions it carries. The answer is invented; it contains no
real interview content.

## Input

```text
Question: How has the housing situation been, and has anything helped?
Answer:   The office cancelled our flat two weeks after they promised it.
          They had no right to do that, and we are still in the shelter.
          My neighbour says the same thing happened to her. A woman from
          the language school sits with me every Thursday and fills in the
          forms, otherwise I would not manage.
```

## Pass A: scopes and evidence

| Ref | Evidence (verbatim) | Scope |
| --- | --- | --- |
| `e1` | The office cancelled our flat two weeks after they promised it | `s1` |
| `e2` | They had no right to do that | `s1` |
| `e3` | we are still in the shelter | `s1` |
| `e4` | A woman from the language school sits with me every Thursday and fills in the forms | `s2` |
| `e5` | otherwise I would not manage | `s2` |

- *My neighbour says the same thing happened to her* creates no scope: it
  reports another person's experience, not the respondent's own evaluation.
- The cancellation, the stated wrong and the ongoing shelter stay in one scope:
  they are cause, judgement and current state of one appraisal.
- The help with the forms is a second scope because the respondent values it
  in its own right; it is credited to a named helper.

Pass A returns only the evidence and this grouping. The scopes are then frozen.

## Pass B: nine variables per scope

| Scope | Focus | Agency | Time | Certainty | Coping | Norm violation | Self-blame | Depletion | Goal relevance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `s1` | `blocked_goal` | `other` | past, present | certain | `low` | 2 | 0 | false | medium |
| `s2` | `benefactor` | `other` | present | certain | `high` | 0 | 0 | false | medium |

## Layer 3: emotion map

Layer 3 reads only the Pass B records:

```text
s1: blocked_goal -> frustration (negative, obstruction band)
s1: negative scope + norm violation 2 + agency "other" -> anger overlay
s2: benefactor -> gratitude (positive, active band)
```

The answer carries the emotions present in at least one scope:

```json
["frustration", "anger", "gratitude"]
```

No intensity is derived, and an answer with two frustration scopes would still
count frustration once.

## Why this example

1. It contains no emotion words, yet every emotion traces to quoted evidence.
2. Anger is added on top of frustration, not instead of it.
3. A third-party report stays uncoded.
4. Material that develops one appraisal stays in one scope.

The machine-readable result is
[`examples/SEG_SYN_001_trace.json`](../examples/SEG_SYN_001_trace.json). A test
re-runs the pipeline and compares the result with this file.
