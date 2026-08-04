# Layer 3 - segment review and aggregation (draft)

Review the complete unit: one moderator question plus one respondent answer.
Use only the validated Layer 2 emotion profile.

Return:

- `valence`: `positive`, `negative`, `mixed`, or `neutral`;
- `emotion_present`: `yes` or `no`;
- `final_emotions`: the merged Layer 2 emotion labels;
- `review.clear`: false if Layer 2 contains unresolved errors;
- `review.ambiguity_flags`: `layer2_errors` when applicable;
- a short review note.

Rules:

1. An empty Layer 2 profile produces `valence: neutral`, `emotion_present: no`,
   and an empty emotion list.
2. Negative and positive emotions together produce `valence: mixed`.
3. Do not invent a neutral emotion label.
4. Preserve the full question and answer.
5. Do not call a result clear when the Layer 2 error list is non-empty.

This is a deterministic draft. The aggregation policy should be reviewed with
human-coded examples before research claims are made.

Return JSON matching `schemas/layer3_segment_review_draft.schema.json`.

