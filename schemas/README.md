# JSON Schema contracts

| Schema | Boundary |
| --- | --- |
| `segment.schema.json` | Input: one interviewer question and one respondent answer |
| `pass_a_scope_lock.schema.json` | Pass A output: evidence items and their grouping into scopes |
| `pass_b_appraisal.schema.json` | Pass B output: exactly the nine appraisal variables per scope |
| `layer3_emotions.schema.json` | Layer 3 output: primary emotion and overlays per scope, emotions present in the answer |

The pipeline validates every boundary against these files at runtime.
