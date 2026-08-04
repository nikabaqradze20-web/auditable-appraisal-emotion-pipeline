# Pass B - appraisal annotation

Use only the evidence and locked scopes returned by Pass A.

Do not create, merge, split, reorder, or rename scopes. For each locked scope,
return:

- `polarity`: `negative` or `positive`;
- `focus`: one allowed appraisal focus;
- `criterion`: the short reason the focus applies;
- `support_refs`: evidence IDs that support the decision;
- `confidence`: `low`, `medium`, or `high`.

Polarity must agree with focus: `threat`, `loss`, `blocked_goal`, and
`dissatisfaction` are negative; `felt_alleviation`, `benefactor`,
`future_possibility`, `specific_object`, and `general_adequacy` are positive.

Use `general_adequacy` only as a last-resort positive focus. Distinguish
`blocked_goal` from simple dissatisfaction: a blocked goal requires that the
speaker is prevented from doing something they want or need.

Return JSON matching `schemas/pass_b_appraisal.schema.json`.

