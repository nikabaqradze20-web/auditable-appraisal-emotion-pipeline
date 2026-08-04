# Pass A - evidence extraction and scope lock

You receive one moderator question and one respondent answer.

Return only the respondent's exact, contiguous evidence quotes and the native
appraisal scopes they support.

Rules:

1. The default is one scope.
2. Split only when the respondent's stance genuinely differs by time, coping,
   or polarity.
3. Keep evidence in source order.
4. Do not paraphrase, fuse, or invent quotes.
5. Do not infer an appraisal from the moderator question alone.
6. Keep respondent stance separate from context such as causes, effects,
   comparisons, and factual updates.
7. An answer may produce zero scopes.

Every evidence ID must be assigned exactly once. Scope IDs are immutable for
Pass B and future layers.

Return JSON matching `schemas/pass_a_scope_lock.schema.json`.

