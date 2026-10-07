# Auditable appraisal-to-emotion pipeline

A two-pass LLM annotation pipeline that codes how respondents evaluate
situations in interview answers, then derives emotions from those codes with
fixed rules. The research version annotated 6,028 answers from a four-wave
qualitative interview panel and was validated against human coding on
development and held-out data.

This repository is a public-safe reference implementation of that design. It
contains the output contracts, validators, emotion map, codebook summaries and
validation results. The model calls are replaced by deterministic stand-ins and
all examples are synthetic, because the interview material is sensitive.

## Results of the research version

| Check | Result |
| --- | --- |
| Consistency: two Pass B runs on the same scopes | at least **91.6%** agreement on every variable (κ, κw or J ≥ .88) |
| Held-out: does the answer contain an appraisal? (model vs human) | **94-96%**, κ .87-.91 |
| Held-out: focus, the variable that decides the emotion | **91.9-94.6%**, κ .903-.935 |
| Held-out: emotions derived from the codes | the model found **92-95%** of the human coder's emotion codes and added about one in ten of its own |
| Re-run of a 10% production sample (647 units) | identical emotion set in **90.0%** of answers; per-emotion κ .835-.972 |
| Weakest variables (held-out, model vs human) | agency 81.1% exact set; goal relevance κw .675-.789 |
| Main source of instability | long answers: identical emotion set in 58.8% of answers over 300 tokens |

All model-human comparisons rest on **one human reference coder** (the
author); agreement between two human coders was not assessed. Full tables,
the validation design and known systematic differences are in
[`docs/VALIDATION.md`](docs/VALIDATION.md).

## Problem

Respondents rarely name their emotions, but they evaluate constantly: they say
what is hard, unfair, better or worrying. Emotion dictionaries miss evaluations
without an emotion word, a supervised classifier would need thousands of
labelled answers that do not exist, and hand-coding nine variables for about
6,400 answers across four waves is slow and hard to keep consistent. Asking a
model for emotion labels directly is simple, but the label cannot be traced to
its reasons, and errors in dividing the answer, coding the appraisal and
choosing the label cannot be separated.

## Approach

The pipeline follows appraisal theories of emotion (Lazarus, 1991; Scherer,
2001): an emotion follows from how a person evaluates a situation. The model
codes the evaluations; it never names an emotion.

| Step | Task | Done by | Output |
| --- | --- | --- | --- |
| Pass A | Divide one answer into appraisal scopes: independent evaluative episodes owned by the respondent | Model, frozen prompt | Zero or more scopes, each defined by verbatim evidence of 1-20 words |
| Pass B | Code nine appraisal variables for every frozen scope | Model, frozen prompt | Focus, agency, time orientation, certainty, coping, norm violation, self-blame, resource depletion, goal relevance |
| Layer 3 | Derive emotions from the codes | Fixed Python rules | One primary emotion per scope, plus an anger overlay |

Each model pass has one narrow task. Pass A never assigns variables and Pass B
never changes scopes, so errors in dividing answers and errors in coding can be
measured separately. Every emotion traces to its appraisal codes and, through
the scope, to quoted evidence that a validator checks by string matching.

## Emotion map

| Focus | Primary emotion | Focus | Primary emotion |
| --- | --- | --- | --- |
| `threat` | fear/anxiety | `felt_alleviation` | relief |
| `loss` | sadness | `benefactor` | gratitude |
| `blocked_goal` | frustration | `future_possibility` | hope |
| `dissatisfaction` | discontent | `specific_object` | liking/enjoyment |
| | | `general_adequacy` | contentment |

- **Anger** is an overlay on a negative scope: norm violation at level 2 or
  higher, and agency that includes another person, institution or group. The
  scope keeps its primary emotion.
- **Self-blame** has an overlay defined in the code but **not analysed**:
  level-2 self-blame was almost absent and not coded consistently between runs.
- **No intensity is derived.** Results record whether an emotion is present in
  an answer, not how strong it is.
- An answer carries an emotion when at least one of its scopes does.

Theory basis, defaults and residual categories: [`docs/CODEBOOK.md`](docs/CODEBOOK.md).

## Traceability example

`SEG_SYN_001` is synthetic:

```text
Question: How has the housing situation been, and has anything helped?
Answer:   The office cancelled our flat two weeks after they promised it.
          They had no right to do that, and we are still in the shelter.
          My neighbour says the same thing happened to her. A woman from
          the language school sits with me every Thursday and fills in the
          forms, otherwise I would not manage.
```

```text
s1  e1 e2 e3 -> blocked_goal, agency other, past+present, coping low, norm violation 2
             -> frustration + anger overlay
s2  e4 e5    -> benefactor, agency other, present, coping high
             -> gratitude

answer_emotions: ["frustration", "anger", "gratitude"]
```

The neighbour's report creates no scope: it is another person's experience,
not the respondent's evaluation. Step by step: [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).

## Research version and this repository

| | Research version | This repository |
| --- | --- | --- |
| Pass A and Pass B | Language model (`claude-opus-4-8`) with frozen, hashed prompts | Deterministic keyword stand-ins |
| Prompts | Full Layer 1 (v3.1) and Layer 2 prompts | Condensed summaries in `prompts/` |
| Layer 3 emotion map | Python rules | Same rules |
| Validators | Blocking checks on every output | Same structural checks |
| Data | 6,028 real answers, access-restricted | Six synthetic answers |
| Validation | Development, held-out and production re-run (see results) | None: the stand-ins are not a classifier |

## Run it

Requires Python 3.10 or newer and `jsonschema`:

```text
pip install -r requirements.txt
python run_demo.py
python -m unittest discover -s tests -v
```

The demo runs six synthetic answers through all three steps and writes the
ignored file `demo_output.json`.

## Project layout

| Path | Contents |
| --- | --- |
| `prompts/` | Summaries of the Pass A and Pass B prompts and their rules |
| `schemas/` | JSON Schema contracts for every boundary |
| `src/emotion_pipeline/` | Stand-in passes, Layer 3 emotion map, validators, schema checks |
| `data/` | Synthetic question-answer fixtures |
| `examples/` | Committed end-to-end trace |
| `docs/` | Codebook, validation results, architecture, traceability walkthrough |
| `tests/` | Contract, emotion-map and end-to-end tests |

## My contribution

I designed the annotation architecture, the coding framework, the scope and
evidence rules, the prompts, the validation design and the error analysis, and
produced the human reference coding. The public implementation translates these
decisions into executable schemas, validators, tests and synthetic examples.
Coding assistance was used during implementation; the analytical framework,
annotation rules and workflow decisions are mine.

## Limits

- The codes describe appraisals and emotions as expressed in interview
  answers, not felt emotion.
- Agreement is measured against one human coder.
- Held-out Pass B results rest on 37 matched scopes, so their intervals are
  wide.
- All coding works on English translations of the answers.
- The code here demonstrates the contracts and the emotion map. It is not a
  validated instrument, and its keyword rules do not generalise to real
  interviews.

## Privacy boundary

Do not commit raw transcripts, exports, API responses, names, contact details,
locations, dates of birth or pilot workbooks. Real data stays outside version
control. Always inspect Git history before making a repository public.
