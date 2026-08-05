# Auditable appraisal -> emotion pipeline

A public-safe reference implementation of a layered annotation workflow for
detecting emotions in segments from interview data. The pipeline creates a
traceable path from exact textual evidence to appraisal codes and, finally, to
segment-level emotion labels.

The purpose of the repository is not to present a finished emotion classifier.
It demonstrates how a complex annotation task can be divided into narrower,
auditable stages with explicit schemas, validation rules, and evidence
requirements.

## Problem

Emotion detection in segments from interview data is difficult because emotions
are often expressed indirectly, depend on context, and may be mixed within the
same segment.

The broader research project contains approximately 8,000 interview segments,
but it does not yet have a sufficiently large set of reliably human-labelled
segments to train and validate a supervised machine-learning classifier.

Large language models provide a practical alternative because they can interpret
context without requiring a large labelled training set. However, asking a model
to assign emotions directly in a single step creates another problem: the output
is difficult to audit and reproduce.

When a label is wrong, it may be unclear whether the model:

- selected the wrong evidence;
- incorrectly divided the segment into situations;
- misinterpreted the respondent's appraisal;
- or applied the wrong emotion rule.

## Approach

The workflow therefore decomposes annotation into several narrower tasks:

1. extract exact evidence from the respondent's answer;
2. identify and lock distinct appraisal scopes;
3. code the appraisal dimensions within each scope;
4. map the validated appraisal codes to emotions;
5. aggregate scope-level emotions into a segment-level profile.

Each stage has a concrete responsibility and a structured output contract.
Later stages cannot silently rewrite the evidence or change the scopes created
earlier in the pipeline.

This design aims to reduce error propagation, make disagreements easier to
diagnose, and improve the reproducibility and reliability of the annotation
process.

The LLM is treated as a constrained annotator within an auditable workflow,
rather than as an opaque end-to-end emotion classifier.

## Research context

This repository is based on an ongoing research project developing an
AI-assisted annotation pipeline for approximately 8,000 segments from
semi-structured interviews.

The broader research workflow covers evidence extraction, appraisal coding,
emotion labelling, and segment-level aggregation. Model outputs are compared
with manual annotations and repeated model runs to evaluate agreement,
stability, recurring errors, and the effects of changes to prompts and coding
rules.

Because the original interview material is sensitive, the public repository
contains only synthetic fixtures. External model calls are replaced with
deterministic stand-ins so that the schemas, layer boundaries, audits, and tests
can be executed without exposing research data.

## My contribution

I designed the annotation architecture, coding framework, evidence and scope
rules, prompt logic, validation strategy, and error-analysis process.

The public implementation translates these research decisions into executable
schemas, audits, tests, and synthetic examples. Coding assistance was used
during implementation, while the analytical framework, annotation rules, and
workflow decisions were developed and reviewed by me.

## Why staged, and why audited

A single-prompt `text -> emotions` call does not show where an error entered the
process. This project separates the main failure points:

- **Scope identity is immutable.** Pass A creates scope IDs. Later stages keep
  the same IDs, count, and order.
- **Every label points back to evidence.** Labels without resolvable support
  references fail validation.
- **Layer 2 is deterministic.** It reads validated appraisal codes rather than
  silently reinterpreting the raw answer.
- **Schemas are executable.** The input and every layer boundary are validated
  against explicit JSON Schema contracts.
- **Sensitive data stays outside the repository.** All committed examples are
  synthetic and clearly separated from the original research material.

## Workflow

| Stage | Sees | Emits | Run fails if |
| --- | --- | --- | --- |
| Pass A - evidence and scope lock | question + answer | exact evidence spans and ordered scopes | a quote is not source text, evidence is unassigned, or the schema fails |
| Pass B - appraisal coding | locked scopes and evidence | focus, polarity, agency, temporal, certainty, coping, ordinals | scope identity changes or a value is outside the contract |
| Layer 2 - emotion mapping | validated appraisal codes | per-scope emotions, intensity, and trace | a focus is unknown or scoring errors remain |

The current implementation is a working draft. Intensity modifiers, derived
emotion gates, and the merged segment profile still require validation against
a human-coded gold set.

The built-in evidence splitter uses generic sentence and conjunction rules. The
canonical example is a teaching fixture, not a set of special-case phrases.

## Traceability example

**`SEG_SYN_001`** is synthetic and contains no real interview content.

```text
Question: How has the housing situation been, and has anything helped?
Answer:   The office cancelled our flat two weeks after they promised it.
          They had no right to do that, and we are still in the shelter.
          My neighbour says the same thing happened to her. A woman from
          the language school sits with me every Thursday and fills in the
          forms, otherwise I would not manage.
```

Evidence extracted:

| Ref | Span | Scope |
| --- | --- | --- |
| `e1` | The office cancelled our flat two weeks after they promised it | `s1` |
| `e2` | They had no right to do that | `s1` |
| `e3` | we are still in the shelter | `s1` |
| `e4` | A woman from the language school sits with me every Thursday and fills in the forms | `s2` |
| `e5` | otherwise I would not manage | `s2` |

The sentence *My neighbour says the same thing happened to her* is deliberately
excluded. It is a third-party report, not the respondent's own stance.

Trace:

```text
e1,e2,e3 -> s1 -> blocked_goal / other / past+present / coping low
                  norm_violation_level 2
                  -> frustration (3)
                  -> anger_indignation (3), derived by gate

e4,e5     -> s2 -> benefactor / other / present / coping high
                  -> gratitude (2)

segment_emotions: {"frustration": 3, "anger_indignation": 3, "gratitude": 2}
```

The saved trace is [`examples/SEG_SYN_001_trace.json`](examples/SEG_SYN_001_trace.json).
The step-by-step walkthrough is in [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).

## Emotion contract

Core map:

| Focus | Emotion |
| --- | --- |
| `threat` | `anxiety_fear` |
| `loss` | `sadness_loss` |
| `blocked_goal` | `frustration` |
| `dissatisfaction` | `mild_negative` |
| `felt_alleviation` | `relief_safety` |
| `benefactor` | `gratitude` |
| `future_possibility` | `hope` |
| `specific_object` | `joy` |
| `general_adequacy` | `contentment` |

Derived emotions are additive and gated in Python:

- `anger_indignation`: norm violation >= 2 plus a blameable agency;
- `shame_guilt`: self-blame >= 2 plus self or in-group agency.

An empty scope list produces an empty emotion set. A neutral segment never
receives an invented neutral emotion.

## Run it

Requires Python 3.10 or newer and the `jsonschema` package:

```text
python run_demo.py
python -m unittest discover -s tests -v
```

Install the runtime dependency with `pip install -r requirements.txt`.

The demo processes six synthetic segments and writes the ignored file
`demo_output.json`.

## Project layout

| Path | Contents |
| --- | --- |
| `prompts/` | provider-neutral contracts for Pass A, Pass B, and Layer 2 |
| `schemas/` | JSON contracts for each boundary |
| `src/emotion_pipeline/` | deterministic passes, scoring, audits, and schema validation |
| `data/` | synthetic question-answer fixtures |
| `examples/` | committed end-to-end trace |
| `docs/` | architecture, traceability, and annotation manual draft |
| `tests/` | contract and end-to-end tests |

## What this is and is not

**Is:** a reviewable baseline for an auditable annotation workflow with
executable interface contracts and runtime schema checks.

**Is not:** a validated measurement instrument, a production classifier, or
evidence that keyword rules generalize. Any real use requires a human-coded
gold set, an independent coder, agreement statistics, and error analysis.
Model output is a noisy measurement, never ground truth.

## Privacy boundary

Do not commit raw transcripts, exports, API responses, names, contact details,
locations, dates of birth, or pilot workbooks. Real data stays outside version
control and outside the synthetic fixtures. Legacy local artifacts are excluded
by [`.gitignore`](.gitignore); always inspect Git history before making a
repository public.

## Attaching a model later

Replace the deterministic Pass A and Pass B stand-ins with model calls that
return the same JSON contracts. Keep Layer 2 deterministic and keep all audits
and tests. If a model-backed layer cannot pass the audits, fix the prompt or
contract rather than weakening the audit.

