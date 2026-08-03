# Layer 2 â€” emotion annotation

Use only validated appraisal scopes. Map each appraisal focus to an emotion without introducing unsupported emotions.

For every scope, return the immutable `scope_id`, one emotion, an intensity, a confidence value, and evidence references.
If evidence is weak, lower confidence rather than inventing evidence.

Return JSON matching `schemas/layer2_emotions.schema.json`.

