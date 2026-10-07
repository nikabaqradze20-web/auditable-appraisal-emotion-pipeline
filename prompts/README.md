# Prompt contracts

Condensed public summaries of the two model prompts used in the research
version:

| File | Research prompt | Task |
| --- | --- | --- |
| `pass_a_scope_lock.md` | Layer 1 prompt (v3.1) | Divide one answer into appraisal scopes, each defined by verbatim evidence |
| `pass_b_appraisal.md` | Layer 2 prompt (frozen) | Code nine appraisal variables for every frozen scope |

The research prompts were frozen before the production run and are identified
by their hashes. They are not published here; these summaries state their rules
and output contracts. Emotions are not produced by a prompt: Layer 3 derives
them in Python (`src/emotion_pipeline/emotion_scoring.py`, `docs/CODEBOOK.md`).
