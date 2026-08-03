# Layer 1.1 â€” appraisal-scheme annotation

Use only the evidence and locked scopes from Layer 1. Do not create, merge, split, or reorder scopes.

For each scope, assign:

- polarity: `negative` or `positive`
- focus: one allowed appraisal focus
- criterion: the concise reason the focus applies
- support_refs: evidence IDs supporting the decision
- confidence: `low`, `medium`, or `high`

Return JSON matching `schemas/layer1_1_appraisal.schema.json`.

