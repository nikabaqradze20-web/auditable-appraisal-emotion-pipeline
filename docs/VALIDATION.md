# Validation and production metrics

All figures come from the research version: the frozen Pass A and Pass B
prompts run with a language model on the full set of interview answers. The
code in this repository uses deterministic stand-ins and has not been
validated. All model-human comparisons rest on **one human reference coder**
(the author); agreement between two human coders was not assessed.

## Data and production run

| Item | Value |
| --- | --- |
| Material | Four-wave qualitative interview panel, three countries, translated into English |
| Respondents / interviews | 143 / 457 |
| Annotated units | 6,410 (a few long answers were split before annotation and recombined afterwards) |
| Valid answers in the analysis | 6,028 (after recombining split answers, excluding 363 minimal answers such as "Yes." and 1 failed annotation) |
| Appraisal scopes | 4,623 |
| Answers with at least one appraisal | 4,099 (68.0%) |
| Scopes per answer | 0: 32.0%; 1: 60.3%; 2: 7.0%; 3 or more: 0.7% |

| Setting | Value |
| --- | --- |
| Model | `claude-opus-4-8`, Anthropic Messages API |
| Maximum output length | 4,000 tokens |
| Retries after a failed call | 2 |
| Temperature, top-p, seed | Not set (API defaults), so two runs on the same input can differ |
| Prompts | Frozen before production and identified by their hashes |

Every output passed a blocking validator before it was accepted:

| Pass | Blocking checks |
| --- | --- |
| Pass A | JSON structure; evidence IDs in sequence; every quote non-empty, 1-20 words and verbatim in the answer; every scope refers to existing evidence without repeats and in text order; every evidence item belongs to exactly one scope; scopes ordered by first evidence item |
| Pass B | One record per Pass A scope with the same IDs in the same order and exactly the required fields; every variable has an allowed value and number of values |

| Outcome of the production run | Units | Valid answers |
| --- | --- | --- |
| Regular production runs | 6,086 | 5,721 |
| Manual input correction, then re-annotation | 149 | 148 |
| Final re-run, unchanged input | 175 | 159 |
| **Total** | **6,410** | **6,028** |

Manual correction repaired the input (separating interviewer and respondent
text, removing transcript metadata, splitting merged turns) and, where needed,
the evidence and scope structure. No Pass B value was edited by hand. The
analysis models were re-estimated without the 148 corrected answers, with the
same results. One coding rule was not enforced during the run: `circumstance`
should stand alone, but 71 production scopes pair it with another agent; the
analysis drops the paired `circumstance`.

## Validation design

| Sample | Answers | Waves | Prompts | Pass A runs | Pass B runs (on the scopes of the first Pass A run) | Model vs human |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 200 | W1-W3, stratified by wave and country | Revised on these answers, then frozen | 2 | 2 | **Fit** |
| Held-out | 50 | W4, stratified by country and topic | Frozen; never seen during development | 3 | 2 | **Validity** |

The held-out answers were human-coded before any model output was seen. Both
Pass B runs code the same scopes, so differences between them come from coding
alone. The held-out sample is stratified, so its agreement is performance on a
W4 test set, not an estimate for the corpus; it contains no answer longer than
238 words.

**Measures.** Agreement (%) is the share coded identically. Cohen's kappa (κ)
corrects for chance agreement. Quadratic-weighted kappa (κw) is used for
ordered scales (coping, norm violation, goal relevance). Exact-set agreement and
mean Jaccard similarity (J) are used for variables with several values
(agency, time orientation, certainty). Chance-corrected coefficients are not
reported for categories with fewer than 10 cases. As a rough guide, .80 or more
indicates strong agreement; Krippendorff (2018) treats .667 as the lowest value
for tentative conclusions. Intervals are 95% bootstrap intervals.

## Pass A: gate and scoping

Gate = does the answer contain an appraisal? Scope count = 0, 1 or 2+.

| Sample | Comparison | Answers | Gate: agreement | Gate: κ | Scope count: agreement | Scope count: κ |
| --- | --- | --- | --- | --- | --- | --- |
| Development | run 1 vs run 2 | 200 | 97.0% | .924 | 94.0% | .894 |
| Development | run 1 vs human | 200 | 95.0% | .879 | 89.5% | .803 |
| Development | run 2 vs human | 200 | 95.0% | .879 | 89.0% | .792 |
| Held-out | between three runs | 50 | 94.0-96.0% | .869-.911 | 90.0-92.0% | - |
| Held-out | each run vs human | 50 | 94.0-96.0% | .871-.913 | 90.0-94.0% | - |

Held-out scope-count κ is not reported because fewer than 10 answers have two
or more scopes. Held-out gate κ intervals are wide (lower bounds .70-.77).

## Pass B: consistency between runs

Two runs on the same scopes agree on at least 91.6% of scopes for every
variable.

| Variable (measure) | Development (167 scopes) | Held-out (40 scopes) |
| --- | --- | --- |
| Focus, % (κ) | 91.6 (.900) | 92.5 (.910) |
| Agency, % exact set (J) | 91.6 (.928) | 92.5 (.925) |
| Time orientation, % exact set (J) | 95.2 (.978) | 97.5 (.988) |
| Certainty, % exact set (J) | 91.6 (.954) | 97.5 (.988) |
| Coping, % (κw) | 93.4 (.917) | 100 (1.000) |
| Norm violation, % (κw) | 98.8 (.978) | 100 (1.000) |
| Goal relevance, % (κw) | 94.6 (.920) | 95.0 (.881) |
| Self-blame, % | 99.4 | 100 |
| Resource depletion, % | 99.4 | 95.0 |

## Pass B: agreement with the human coder

Ranges across the two runs, on matched scopes (development: 147; held-out: 37).

| Variable (measure) | Development (fit) | Held-out (validity) |
| --- | --- | --- |
| Focus, % (κ) | 90.5-91.2 (.887-.895) | 91.9-94.6 (.903-.935) |
| Agency, % exact set (J) | 85.7 (.867-.871) | 81.1 (.824-.838) |
| Time orientation, % exact set (J) | 91.8-93.9 (.960-.971) | 91.9 (.964) |
| Certainty, % exact set (J) | 92.5 (.954-.959) | 94.6-97.3 (.973-.986) |
| Coping, % (κw) | 93.2-95.9 (.895-.941) | 86.5 (.907) |
| Norm violation, % (κw) | 95.9-96.6 (.928-.938) | 100 (1.000) |
| Goal relevance, % (κw) | 87.8-89.8 (.818-.852) | 86.5-91.9 (.675-.789) |
| Self-blame, % | 99.3 | 100 |
| Resource depletion, % | 98.0-98.6 | 97.3-100 |

- **Focus**, which decides the primary emotion, agrees as well on held-out
  answers as on development answers (held-out κ intervals [.786, 1.000] and
  [.828, 1.000]).
- **Agency is the weakest variable.** The model agrees with itself more than
  with the human coder. The enemy side and other concrete actors are rarely
  confused (2 of 79 matched scopes); the main disagreement is circumstance coded
  as the enemy side (9 of 81).
- **Goal relevance** is calibrated differently: the model rated it higher in 16
  of 18 development disagreements. It does not enter the emotion map.
- **Self-blame and depletion** agreement mostly reflects scopes where both
  sides code them absent.

## Derived emotions against the human coder

Emotions derived from the human codes and from each model run with the same
fixed map, per answer.

| | Development (200 answers) | Held-out (50 answers) |
| --- | --- | --- |
| Emotion codes, human | 156 | 38 |
| Emotion codes, model runs | 172 / 171 | 42 / 41 |
| Human codes also found by the model | 91-92% | 92-95% |
| κ for emotions with at least 10 human-coded answers | .74-.88 | - |

The model finds almost all emotions the human coder finds and adds about one
code in ten of its own, mostly fear (26 vs 21 development answers), frustration
(45-46 vs 40), hope (7-8 vs 4) and relief (7-8 vs 5); it codes contentment less
often (18 vs 21). Most variable disagreements do not change the emotion: among
scopes with at least one Pass B disagreement against the human coder, the
derived emotion is the same in 79.2% (development) and 77.8-81.2% (held-out).

## Production re-run of a 10% sample

647 production units (a random 10% across all batches, covering all wave and
country cells) were annotated again from scratch with the frozen prompts. This
measures consistency, not correctness.

| Step | Measure | Agreement |
| --- | --- | --- |
| Pass A | Gate | 98.6%, κ .970 [.948, .987] |
| Pass A | Scope count | 93.8%, κ .891 [.858, .921] |
| Pass B (460 matched scopes) | Focus | 89.4%, κ .875 |
| | Agency | 91.7% exact set, J .923 (agent vs circumstance κ .868) |
| | Time orientation | 89.8% exact set, J .951 |
| | Certainty | 95.4% exact set, J .965 |
| | Coping | 92.0%, κw .890 |
| | Norm violation | 97.8%, κw .938 |
| | Goal relevance | 93.3%, κw .880 |
| | Self-blame | 5 and 5 positive scopes, 2 shared: **not reliable, not analysed** |
| | Resource depletion | 17 and 17 positive scopes, 16 shared |
| | All nine variables identical | 63.9% |
| Emotion mapping (scopes) | Primary emotion | 89.4%, κ .875 |
| | Emotion band | 93.3%, κ .907 |
| | Anger overlay | 27 positive scopes in each run, 24 shared, κ ≈ .882 |
| Emotion mapping (answers) | Identical emotion set, all 647 units | **90.0%** [87.6, 92.2], mean J .917 |
| | Identical emotion set, units with any emotion | 84.3%, mean J .870 |

Presence of each emotion in an answer (κ): fear/anxiety .877, sadness .934,
frustration .864, discontent .885, anger .867, relief .853, gratitude .972,
hope .835, liking/enjoyment .836, contentment .866.

Of the 49 scopes where focus differed, 38 (77.6%) stayed on the same side
(negative or positive). The two main confusions are frustration vs discontent
and liking/enjoyment vs contentment.

**Answer length is the main source of instability.**

| Answer length (tokens) | Identical scope count | Identical emotion set |
| --- | --- | --- |
| 1-99 | 94.9-98.3% | 93.4% |
| 100-199 | 91.6% | 83.2% |
| 200-299 | 68.6% | 74.3% |
| 300 or more | 64.7% | 58.8% |

## Systematic differences and how the analysis handles them

| Pattern | Evidence | Handling |
| --- | --- | --- |
| The model finds more appraisals than the human coder | 9 of 10 gate disagreements (development); about 4 pp more evaluative answers, roughly constant across waves | Wave differences unaffected if the tendency is constant |
| The model splits answers more finely | 167 and 166 scopes vs 148 (+12-13%) | Outcomes record presence per answer, not scope counts |
| Some emotions coded more often | Fear, frustration and hope slightly higher, contentment slightly lower | Results read as changes; per-wave check against human coding |
| Goal relevance rated higher | 16 of 18 development disagreements | Not in the emotion map; read for change, not level |
| Agency agreement lower in later waves | W1 93-95%, W2 85%, W3 79-81%, W4 81% of matched scopes | The main attribution finding is, if anything, understated |
| Circumstance paired with an agent | About 2-3% of model scopes; 71 in production | Paired circumstance dropped |
| Long answers less consistent | Identical emotion set in 58.8% of 300+ token answers | Answer length controlled; check without 300+ word answers |

## What the checks do not establish

- **Agreement between two humans.** With one reference coder, it is unclear how
  much remaining disagreement is model error and how much is ambiguity two
  humans would also disagree on.
- **Error rates per wave, emotion and country.** Checked only in the small
  human-coded samples, which can reveal large shifts, not small ones.
- **Precision of held-out Pass B results.** They rest on 37 matched scopes; the
  lower bound is .786 for focus κ and .358 for goal relevance κw.
- **Rare codes.** Self-blame and depletion have too few positive cases for
  chance-corrected coefficients.
- **What the codes mean.** The checks concern the coding, not the construct.
  They do not show that expressed emotions match felt emotions or that the map
  from appraisals to emotions is correct. Intensity is not measured.
