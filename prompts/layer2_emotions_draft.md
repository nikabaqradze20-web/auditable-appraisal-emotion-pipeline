# Layer 2 - deterministic emotion scoring (draft)

This layer is pure Python. It consumes validated Pass B appraisal scopes and
does not call a model or re-read evidence text.

Rules:

1. Score each scope separately.
2. Map one appraisal focus to one core emotion.
3. Add derived emotions only when the Python gates fire.
4. Merge labels by union and keep maximum intensity.
5. Empty scopes produce no emotions.
6. Unknown focus or invalid attributes produce errors; never use a silent default.

The current intensity modifiers and emotion gates are provisional and must be
validated against a human-coded gold set.

Return JSON matching `schemas/layer2_emotions_draft.schema.json`.

