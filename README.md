# Auditable appraisal -> emotion pipeline

A small, public-safe reference implementation of a staged annotation workflow
that turns one moderator question plus one respondent answer into segment-level
emotion labels, with a complete evidence trail from quote to label.

The point of this repository is **the contracts and the audits, not the
classifier**. The layer functions are deterministic and offline so the
interfaces can be executed and tested before any model is attached. All
fixtures are synthetic.

## Why staged, and why audited

A single-prompt "text -> emotions" call is difficult to audit. When a label is
wrong, there is no way to tell whether the system misread the quote, invented a
second situation, or applied the wrong emotion rule.

This project separates those failure modes:

- **Scope identity is immutable.** Pass A creates scope IDs. Later stages keep
  the same IDs, count, and order.
- **Every label points back to evidence.** Labels without resolvable support
  references fail validation.
- **Layer 2 is deterministic.** It reads appraisal codes and does not quietly
  reinterpret the raw answer.

## Workflow

| Stage | Sees | Emits | Run fails if |
| --- | --- | --- | --- |
| Pass A - evidence and scope lock | question + answer | exact evidence spans and ordered scopes | a quote is not source text or evidence is unassigned |
| Pass B - appraisal coding | locked scopes and evidence | focus, polarity, agency, temporal, certainty, coping, ordinals | scope identity changes or a value is outside the contract |
| Layer 2 - emotion mapping | validated appraisal codes | per-scope emotions, intensity, and trace | a focus is unknown or scoring errors remain |
| Layer 3 - segment review | complete question-answer plus merged emotions | final emotions, valence, and emotion presence | question-answer text changes or neutral handling is wrong |

The current implementation is a working draft. Intensity modifiers, derived
emotion gates, and Layer 3 aggregation still require validation against a
human-coded gold set.

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

final_emotions: ["frustration", "anger_indignation", "gratitude"]
valence: mixed
emotion_present: yes
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

Requires Python 3.10 or newer. No external packages are required:

```text
python run_demo.py
python -m unittest discover -s tests -v
```

The demo processes six synthetic segments and writes the ignored file
`demo_output.json`.

## Project layout

| Path | Contents |
| --- | --- |
| `prompts/` | provider-neutral contracts for Pass A, Pass B, Layer 2, and Layer 3 |
| `schemas/` | JSON contracts for each boundary |
| `src/emotion_pipeline/` | deterministic passes, scoring, audits, and review |
| `data/` | synthetic question-answer fixtures |
| `examples/` | committed end-to-end trace |
| `docs/` | architecture, traceability, and annotation manual draft |
| `tests/` | contract and end-to-end tests |

## What this is and is not

**Is:** a reviewable baseline for an auditable annotation workflow with
executable interface contracts.

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

