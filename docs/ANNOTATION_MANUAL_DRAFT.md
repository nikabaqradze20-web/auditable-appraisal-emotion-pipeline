# Annotation manual draft

**Status:** Draft for review. This manual describes the intended research design;
the current repository implementation is still a smaller illustrative baseline.

## What matters most

The project is worth doing if its goal is narrow:

> Reduce scope and emotion annotation variance, especially false emotion firing,
> by forcing every emotion to pass through an evidence-backed appraisal scope.

It should not yet claim to measure the respondent's true psychological state.
LLM annotations are noisy measurements and require human-coded validation.

## Unit of analysis

One unit contains exactly:

```text
one moderator question + one respondent answer
```

The question supplies context. Appraisal evidence must come from the respondent
answer unless a separate contextual field is explicitly marked as such.

## Pipeline

| Layer | Job | Main safeguard |
| --- | --- | --- |
| 1 | Extract verbatim evidence and create native scopes | Exact evidence and scope rules |
| 1.1 | Annotate appraisal attributes | Schema and gate validation |
| 2 | Score emotions scope by scope | CORE gates; no free reinterpretation |
| 3 | Review the complete question-answer segment | Final aggregation and ambiguity note |

The default is **one scope**. Multiple scopes are allowed only when the
respondent's stance genuinely differs by time, coping, or polarity.

## Layer 1: scope and appraisal fields

### Segment-level fields

| Field | Allowed values | Rule |
| --- | --- | --- |
| `goal_relevance` | `low`, `medium`, `high` | Relevance of the answer to the respondent's goal |
| `valence` | `negative`, `neutral`, `positive`, `mixed` | Must be recoverable from scope-level appraisals |

`mixed` requires at least one positive and one negative scope. Segment valence
must never contradict the scopes.

### Scope-level fields

| Field | Allowed values | Purpose |
| --- | --- | --- |
| `focus` | see focus table | What the respondent is appraising |
| `agency` | `self`, `other`, `in_group`, `out_group`, `circumstance` | Who or what causes or controls the situation |
| `certainty` | `certain`, `uncertain`, `hypothetical` | Epistemic status of the appraisal |
| `temporal` | `past`, `present`, `future` | Time explicitly supported by evidence |
| `coping` | `zero`, `low`, `medium`, `high` | Remaining coping capacity |
| `norm_violation_level` | `0`, `1`, `2`, `3` | Strength of perceived wrongdoing |
| `self_blame_level` | `0`, `1`, `2`, `3` | Strength of blame directed at self or in-group |
| `resource_depletion` | `true`, `false` | Internal exhaustion, not an external obstacle |

Agency is capped at **two values per scope**.

## Evidence rules

### Required

- Evidence must be verbatim, contiguous text from the respondent answer.
- A validator may accept only an explicitly defined fuzzy match.
- Fused or invented quotes fail validation.
- Every appraisal and emotion must have support references.
- Evidence IDs are assigned once and remain immutable.

### Irony

Do not infer irony. The `irony_suspected` field is intentionally absent.

## Scope-splitting rules

### Keep one scope when

- multiple objects share the same stance;
- the feeling and time are the same;
- several facts support one appraisal;
- a positive exception is part of one overall negative trajectory.

### Split into multiple scopes only when

| Trigger | Example pattern |
| --- | --- |
| Time changes | past fear, present relief |
| Coping changes | managed before, exhausted now |
| Polarity changes | negative obstacle, positive outcome |

Do not split simply because the answer mentions several people, places, or
events.

## Focus decision rules

### Negative focus

| Focus | Use when | Do not use when |
| --- | --- | --- |
| `threat` | Possible harm is salient | Risk is only reported factually with no respondent stance |
| `loss` | A valued object or condition is gone or degraded | The object is merely unavailable temporarily without loss stance |
| `blocked_goal` | The speaker is prevented from doing something they want or need | The speaker only dislikes an outcome |
| `mild_dissatisfaction` | The speaker gives a mild negative verdict without being blocked | There is a clear blocked goal or severe wrongdoing |

### Positive focus ladder

Use the first applicable focus in this order:

```text
felt_alleviation
    -> benefactor
    -> future_possibility
    -> specific_object
    -> general_adequacy
```

| Focus | Required evidence |
| --- | --- |
| `felt_alleviation` | Prior acute burden ended and the speaker describes release or relief |
| `benefactor` | Another party provided valued help and receives positive credit |
| `future_possibility` | Genuine positive future anticipation, not desire alone |
| `specific_object` | A specific object or activity receives positive valuation |
| `general_adequacy` | Overall current condition receives a positive verdict |

`general_adequacy` is the last resort. Do not use generic positivity as a
shortcut.

## Agency rules

Before assigning `circumstance`, ask:

> Is there a real person, group, or institution causing this?

- Yes: use `other`, `out_group`, or `in_group` as appropriate.
- No: use `circumstance` for a genuinely impersonal condition.
- Never use `circumstance` as a default when the actor is unclear.

## Coping and depletion

Ask: **Has the speaker tried and failed, with options running out?**

| Situation | Coping |
| --- | --- |
| Manages freely | `high` |
| Obstacle exists but the speaker is still moving | `medium` |
| Tried, failed, and few options remain | `low` |
| Exhausted or does not know who can help | `zero` |

`resource_depletion = true` only means internal exhaustion. An external blocker
alone is not depletion.

## Temporal rules

Add `present` only when the evidence contains a present-tense clause showing:

- somatic now;
- stance now; or
- state now.

Do not add `present` merely because a past event is vivid or severe.

## Ordinal rules

| Level | Norm violation | Self-blame |
| --- | --- | --- |
| 0 | No wrongdoing | No self-blame |
| 1 | Mild complaint or criticism | Mild self-criticism |
| 2 | Clear wrongdoing or meaningful blame | Clear self/in-group blame |
| 3 | Severe, repeated, or atrocity-level wrongdoing | Severe or repeated self/in-group blame |

`self_blame_level >= 2` requires `self` or `in_group` in `agency`. This is a
programmatic gate, not a prompt suggestion.

## Layer 2 emotion rules

Layer 2 reads Layer 1 scopes separately. It may not override Layer 1 with a
new free-form interpretation.

| Appraisal focus | Default emotion |
| --- | --- |
| `threat` | `anxiety_fear` |
| `loss` | `sadness_loss` |
| `blocked_goal` | `frustration` |
| `mild_dissatisfaction` | mild negative, low intensity |
| `benefactor` | `gratitude` |
| `felt_alleviation` | `relief_safety` |
| `future_possibility` | `hope` |
| `specific_object` | `joy` |
| `general_adequacy` | `contentment` |

Derived emotions are additive:

| Condition | Add |
| --- | --- |
| `norm_violation_level >= 2` plus `other`, `out_group`, or `in_group` | `anger_indignation` |
| `self_blame_level >= 2` plus `self` or `in_group` | `shame_guilt` |

For the segment, merge by union of active labels and keep maximum intensity.
The merge must retain the contributing scope and evidence IDs.

## Validator requirements

Validators must enforce:

1. exact or approved fuzzy evidence matching;
2. JSON schema and allowed-label checks;
3. no fused or non-verbatim quotes;
4. default-one-scope and split-trigger rules;
5. maximum two agency values;
6. valence recoverability and mixed-valence requirements;
7. the three-trigger temporal rule;
8. `resource_depletion` semantics;
9. self-blame agency gates;
10. CORE emotion conditions programmatically.

## Gold-standard validation

Before scaling, create a human-coded synthetic or de-identified gold set with
expected outputs for every layer. Include:

- single-scope positive and negative cases;
- genuine mixed-valence cases;
- time changes;
- coping changes;
- blocked goal versus dissatisfaction;
- benefactor versus circumstance;
- explicit self-blame;
- norm violation;
- no-emotion and ambiguous cases.

Report exact agreement, per-label precision/recall, scope-count agreement, and
false emotion firing. Do not report only overall accuracy.

## Current implementation gap

The repository's current demo does **not** yet implement every rule above.
Notable gaps are:

- it uses `dissatisfaction` rather than the proposed `mild_dissatisfaction`;
- it does not yet expose segment-level `valence` and `goal_relevance`;
- its ordinals currently stop below the proposed level 3;
- fuzzy matching and CORE gates are not fully implemented;
- the emotion names are simplified (`fear`, `relief`, and so on).

These are deliberate next steps, not reasons to hide the prototype's limits.

## What should not change yet

- Do not add more LLM layers until the Layer 1 scope rules are stable.
- Do not send sensitive refugee interviews to an API before privacy approval.
- Do not call model output ground truth.
- Do not publish real transcripts or pilot outputs.

## What I should do next

1. Review and approve the label definitions and focus decision rules.
2. Add a small human-coded gold set with expected Layer 1 and Layer 2 outputs.
3. Upgrade the schemas and validators to enforce the approved rules.
4. Re-run the pilot and measure false emotion firing before adding model calls.

