# Architecture

```text
interviewer question + respondent answer
        |
        v
Pass A: appraisal scopes + verbatim evidence          (model in research; stand-in here)
        | validator: verbatim 1-20 word quotes, every item in exactly one scope, order
        v
frozen scopes
        |
        v
Pass B: nine appraisal variables per scope            (model in research; stand-in here)
        | validator: one record per scope, same IDs and order, allowed values only
        v
Emotion mapping: fixed rules in Python               (identical in research and here)
        | check: primary emotion follows focus, anger only on negative scopes
        v
emotions present in the answer
```

At each boundary, `src/emotion_pipeline/schema_validation.py` validates the
object against the matching file in `schemas/` before the next step. The
schemas are executable contracts. Pass B's schema rejects any field beyond the
nine variables, so it cannot return an emotion label, a reason or a confidence
score.

## What runs where

| Step | Research version | This repository |
| --- | --- | --- |
| Pass A | Frozen Pass A prompt, language model | Keyword and clause rules (`layers.py`) |
| Pass B | Frozen Pass B prompt, language model | Keyword rules with codebook defaults (`layers.py`) |
| Emotion mapping | Python rules | Same map (`emotion_mapping.py`) |
| Validators | Blocking checks on every output | Same structural checks (`audits.py`, `schemas/`) |
| Data | Real interview answers, access-restricted | Six synthetic answers (`data/`) |

The stand-ins exist so that the contracts, validators and emotion map can be
run and tested without a model or real data. They are not a classifier.

## Design principles

- Model output is a measurement with error, validated against human coding.
- Each model pass has one narrow task: Pass A never assigns variables, Pass B
  never changes scopes.
- The model never names an emotion; a fixed, inspectable map derives emotions.
- Every emotion traces to appraisal codes and, through the scope, to verbatim
  evidence that a validator can check by string matching.
- Results record whether an emotion is present in an answer, not how many
  scopes carry it.
- Sensitive source material stays outside the repository.

## Attaching a model

Replace `pass_a_scope_lock` and `pass_b_appraisal` in `layers.py` with model
calls that return the same JSON contracts. Keep the emotion mapping deterministic and keep
all validators and tests. If a model-backed pass cannot pass the validators,
fix the prompt or the contract rather than weakening the validator. Freeze and
hash the prompts before any production run, and validate on a held-out sample
the prompts have not seen (see `docs/VALIDATION.md`).
