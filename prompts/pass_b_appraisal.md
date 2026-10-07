# Pass B prompt: nine appraisal variables (summary)

You receive the answer, the interviewer's question, the evidence items and the
frozen scopes. Code each scope from its own evidence; use the rest of the
answer only to read that evidence correctly. Do not add, remove, split, merge
or reorder scopes, and do not introduce new evidence. Return exactly one record
per scope, in the same order.

| Variable | Question | Values | Per scope |
| --- | --- | --- | --- |
| `focus` | What kind of relation to the situation does the respondent express? | negative: `threat`, `loss`, `blocked_goal`, `dissatisfaction`; positive: `felt_alleviation`, `benefactor`, `future_possibility`, `specific_object`, `general_adequacy` | exactly 1 |
| `agency` | Who or what brought the situation about? | `self`, `other`, `in_group`, `out_group`, `circumstance` | 1-2 |
| `temporal` | When is the appraised situation located? | `past`, `present`, `future` | 1-3 |
| `certainty` | How settled is it? | `certain`, `uncertain`, `hypothetical` | 1-2 |
| `coping` | Can the respondent manage, obtain or keep it? | `zero`, `low`, `medium`, `high` | 1 |
| `norm_violation_level` | Does the respondent condemn an actor or action as wrong? | 0-3 | 1 |
| `self_blame_level` | Does the respondent attribute fault to themselves? | 0-2 | 1 |
| `resource_depletion` | Does the respondent express internal exhaustion? | true, false | 1 |
| `goal_relevance` | How much does this matter decide for an important concern? | `low`, `medium`, `high` | 1 |

Key rules:

- **Order.** Decide focus first, then agency, time orientation, certainty,
  coping, the three additional variables and goal relevance. A later variable
  may not change the focus.
- **Focus ladders.** The negative ladder applies while the adversity governs
  the scope; the positive ladder when it has ended and the respondent takes a
  positive stance on the present. Take the first category that fits. The
  residual categories, `dissatisfaction` and `general_adequacy`, come last.
  Most categories need expressed evidence, for example a named helper for
  `benefactor` and an open, concrete path for `future_possibility`.
- **Agency** is the source, not blame. Circumstance is not a shortcut for an
  unnamed actor and only stands alone. An act of war is coded `out_group`.
  Host populations are never `out_group`.
- **Time** records every period the evidence expresses. `present` needs a
  present-tense felt state, evaluation or condition.
- **Coping** describes where things stand at the scope's endpoint, not effort
  or feelings. High coping never turns a negative focus positive.
- **Norm violation, self-blame and depletion** default to absent. Harm is not
  wrongdoing.
- **Goal relevance** starts at `medium`. `high` needs an explicit statement:
  no alternative, a stated consequence, an ongoing danger, or an inability to
  function.

Return the nine variables and nothing else: no reasons, confidence, valence,
emotion labels or intensity.

Return JSON matching `schemas/pass_b_appraisal.schema.json`.
