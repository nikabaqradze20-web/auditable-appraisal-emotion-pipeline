# Codebook summary

This file summarises the measurement design of the research version. The rules
for the two model passes are in `prompts/`; this file covers the units, the
defaults that matter for reading results, and the emotion map.

## What is measured

Appraisal as the respondent expresses it in the interview: not felt emotion,
physiological state or unexpressed evaluation. The interviews were translated
into English before annotation, so all coding works on the English text.

| Level | Unit | Produced by | Output |
| --- | --- | --- | --- |
| Appraisal scope | Respondent answer | Pass A prompt, language model | Zero or more scopes, each defined by verbatim evidence |
| Appraisal variables | Scope | Pass B prompt, language model | Nine coded variables per scope |
| Emotion labels | Scope | Emotion mapping, Python rules | Primary emotion and overlays |
| Not operationalised | - | - | Intensity; emotions outside the map |

Two design rules follow from treating model output as measurement with error:

- **Each model pass has one narrow task.** Pass A never assigns variables;
  Pass B never changes scopes. Errors in unitising and in coding can therefore
  be measured separately.
- **The model never names an emotion.** Emotions are computed from the coded
  appraisals by a fixed map, so every label can be traced to its appraisal
  codes and, through the scope, to verbatim evidence.

## Pass B defaults

Several rules set a value when the evidence is silent. They matter for reading
results.

| Default | Consequence |
| --- | --- |
| Coping: a negative scope without information is `medium`; a positive scope is `high` | "Low or no coping" requires explicit evidence and is a lower bound |
| Norm violation and self-blame are 0; depletion is false | Moral judgement, self-blame and exhaustion are coded conservatively |
| Goal relevance starts at `medium` | High goal relevance requires an explicit statement |
| Agency: no attributed cause is `circumstance` | Circumstance covers impersonal causes and evaluations with no stated cause |

## Emotion mapping

Each focus category maps to one primary emotion. Valence is the side of the
focus ladder. Bands group emotions with a similar appraisal structure and are
used only as a reliability measure.

| Focus | Primary emotion | Valence | Band | Basis in appraisal theory |
| --- | --- | --- | --- | --- |
| `threat` | fear/anxiety | negative | threat | Direct (Lazarus, 1991) |
| `loss` | sadness | negative | loss | Direct (Lazarus, 1991) |
| `blocked_goal` | frustration | negative | obstruction | Other models (Scherer, 2001; Roseman et al., 1996) |
| `dissatisfaction` | discontent | negative | obstruction | Residual category |
| `felt_alleviation` | relief | positive | settled | Direct (Lazarus, 1991) |
| `benefactor` | gratitude | positive | active | Other models (Ortony et al., 1988) |
| `future_possibility` | hope | positive | active | Direct (Ortony et al., 1988; Lazarus, 1991) |
| `specific_object` | liking/enjoyment | positive | active | Other models (Ortony et al., 1988) |
| `general_adequacy` | contentment | positive | settled | Residual category |

**Anger overlay.** Added to a negative scope when norm violation is at level 2
or higher and agency includes `other`, `out_group` or `in_group`. Anger
therefore needs both a clear wrong and a responsible person, institution or
group. An angry scope keeps its primary emotion.

**Self-blame overlay.** Defined (negative scope, self-blame at level 2, agency
includes `self` or `in_group`) but **not analysed**: level-2 self-blame is
almost absent and was not coded consistently between runs.

**Residual categories.** Discontent and contentment catch clearly negative or
positive verdicts that pass no specific test. A rise in discontent means more
negative verdicts without a danger, a loss or a blocked pursuit, not a rise in
one specific feeling.

**From scopes to answers.** An answer carries an emotion when at least one of
its scopes does. Results record presence per answer, not the number of scopes,
because scope counts depend on how Pass A divided the answer.

## What the map assumes

- Each emotion is the one implied by the appraisal, not a separately observed
  feeling. Results refer to emotions as expressed in interview answers.
- Only the nine primary emotions and anger are identified; others, such as
  pride or disgust, are not.
- **No intensity is derived.** An intensity measure was planned but could not be
  developed and validated within the project.
- Emotions are never analysed against the variables they are built from.
