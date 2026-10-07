# Prompt contracts

Condensed public summaries of the two model prompts used in the research
version:

| File | Research prompt | Task |
| --- | --- | --- |
| `pass_a_scope_lock.md` | Pass A prompt | Divide one answer into appraisal scopes, each defined by verbatim evidence |
| `pass_b_appraisal.md` | Pass B prompt | Code nine appraisal variables for every frozen scope |

The research prompts were frozen before the production run and are identified
by their hashes. They are not published here; these summaries state their rules
and output contracts. Emotions are not produced by a prompt: the emotion mapping
derives them in Python (`src/emotion_pipeline/emotion_mapping.py`, `docs/CODEBOOK.md`).
