# Layer 1 â€” appraisal extraction and scope lock

You receive one synthetic or privacy-filtered moderator question and one respondent answer.

Tasks:

1. Extract only exact, contiguous evidence quotes from the respondent answer.
2. Create independent appraisal scopes in the order of their first stance evidence.
3. Separate respondent stance from context such as causes, effects, comparisons, and factual updates.
4. Preserve the text and scope identity for later layers.

Rules:

- Do not infer an appraisal from the moderator question alone.
- Do not paraphrase evidence quotes.
- An answer may produce zero scopes.
- Every evidence item must be assigned to exactly one scope or context item.

Return JSON matching `schemas/layer1_scope_lock.schema.json`.

