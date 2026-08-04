# Architecture and roadmap

## Implemented now

```text
question + answer
        |
        v
Pass A: exact evidence + native scope lock
        | audit: quote and assignment integrity
        v
Pass B: appraisal polarity, focus, criterion, support
        | audit: immutable scope identity and allowed labels
        v
validated appraisal packet
        |
        v
Layer 2 draft: deterministic emotion scoring per scope
        | audit: identity, errors, and intensity bounds
        v
provisional emotion profile
```

Pass B cannot create, merge, split, reorder, or rename Pass A scopes.

## Planned later

```text
provisional emotion profile
        |
        v
Layer 3 draft: whole-segment review and valence aggregation
```

Layer 2 and Layer 3 are working drafts. Their intensity modifiers, derived
gates, and valence aggregation need an approved emotion manual and a human-coded
gold set before they should be treated as reliable.

## Design principles

- Evidence before labels.
- Scope identity is immutable after Pass A.
- Missing evidence is reported, not silently filled.
- The moderator question does not create respondent appraisal evidence.
- LLM output is a noisy measurement, not ground truth.
- Sensitive source material stays outside the public repository.

## Model-backed extension

A future adapter can call an LLM for each pass, but it should keep the prompts
versioned, require structured JSON, validate every response, and record model
metadata separately from annotation text. The current deterministic rules are
only a transparent contract test.

## Validation needed before scaling

Add a human-coded gold set containing single-scope, mixed-polarity, temporal,
coping, agency, blocked-goal, dissatisfaction, and no-appraisal cases. Report
scope-count agreement, per-label precision/recall, and false-label rates.

