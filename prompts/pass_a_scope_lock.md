# Pass A prompt: appraisal scopes and evidence (summary)

You receive one interviewer question and one respondent answer. Decide how many
appraisal scopes the answer holds and which words belong to each. Assign no
variables.

An appraisal is a respondent-owned evaluative episode: the respondent asserts or
endorses an evaluation of a state of affairs that matters to them.

1. **Gate.** Create a scope only for an evaluation whose source is the
   respondent. Another person's evaluation, merely reported, is information.
   A difficult condition described without stance is information. The
   interviewer's question may help interpret the answer but never supplies an
   evaluation. A turn without a respondent-owned evaluation gets zero scopes;
   zero is a coded outcome.
2. **One governing episode.** Every turn that passes the gate starts with one
   scope, organised around the main evaluative concern of the whole answer.
3. **Attach by default.** Material that works as cause, obstacle, condition,
   consequence, burden, coping response, workaround, route, subgoal,
   comparison, qualification or trajectory phase is attached to the appraisal
   it develops, even when it has its own object, strong wording, a different
   time or the opposite polarity. Material whose function is unclear is
   attached.
4. **Second scope only for a second evaluative centre.** Open another scope
   only when all four hold: the respondent evaluates the candidate; it is
   another evaluative centre; its significance is not exhausted by a function
   inside an existing appraisal; it matters to the respondent in its own right.
5. **What does not split.** A change of object, actor, time, polarity or
   manageability does not by itself create a scope. Do not split to make later
   coding cleaner. Standing conditions, trajectories, comparisons and
   mitigations stay in one scope. An evaluation the respondent explicitly
   withdraws creates no scope.

Evidence is extracted after the scope structure is fixed. Each item is a
verbatim, contiguous span of the respondent's words, 1 to 20 words long, and
genuine support for its scope. Never quote the interviewer; never paraphrase,
correct, complete or fuse quotes. Within a scope, quote in this order of
priority: evaluative core, cause or obstacle, coping response or outcome,
explicit time marker, present-tense stance or state clause.

Return only the evidence items and their grouping into scopes, ordered by first
appearance in the answer: no labels, reasons or summaries. The scopes are then
frozen for Pass B.

Return JSON matching `schemas/pass_a_scope_lock.schema.json`.
