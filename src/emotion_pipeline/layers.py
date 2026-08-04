"""Simple, deterministic implementations of Pass A and Pass B.

The functions are intentionally conservative. They are a runnable baseline for
testing scope and appraisal contracts, not a replacement for human annotation
or an LLM-based production annotator. The evidence splitter uses generic
sentence and clause rules; it is not tuned to one fixture's exact wording.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import Segment


FOCUS_RULES: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("threat", ("worried", "afraid", "unsafe", "danger", "risk"), "negative", "possible harm is salient"),
    ("loss", ("lost", "gone", "missing"), "negative", "a valued object or condition is absent"),
    ("blocked_goal", ("cannot", "can't", "unable", "stuck", "delay", "no place", "cancelled", "still in the shelter", "no right"), "negative", "a desired outcome is obstructed"),
    ("dissatisfaction", ("disappointed", "frustrated", "unhappy", "terrible", "poor"), "negative", "the current outcome receives a negative verdict"),
    ("felt_alleviation", ("relieved", "relief", "burden lifted"), "positive", "an acute burden is described as ended"),
    ("benefactor", ("helped", "support", "grateful", "thank", "woman from", "sits with me", "fills in the forms", "would not manage"), "positive", "another party provided valued help"),
    ("future_possibility", ("hope", "hopefully", "plan to", "will be able", "look forward"), "positive", "a possible future gain is anticipated"),
    ("specific_object", ("love", "like", "enjoy"), "positive", "a specific object receives positive valuation"),
    ("general_adequacy", ("works well", "good", "comfortable", "satisfied"), "positive", "the overall current condition receives a positive verdict"),
)

RELEVANCE_BY_FOCUS = {
    "threat": "high",
    "loss": "high",
    "blocked_goal": "high",
    "dissatisfaction": "medium",
    "felt_alleviation": "medium",
    "benefactor": "medium",
    "future_possibility": "medium",
    "specific_object": "medium",
    "general_adequacy": "low",
}

def split_sentences(text: str) -> list[str]:
    return [
        part.strip().rstrip(".!?")
        for part in re.split(r"(?<=[.!?])\s+", text.strip())
        if part.strip()
    ]


def _evidence_units(sentence: str) -> list[str]:
    """Split a sentence into evidence-bearing clauses when conjunctions mark them."""

    clauses = [
        re.sub(r"^(?:and|but)\s+", "", part.strip(), flags=re.IGNORECASE)
        for part in re.split(r",\s+(?=(?:and|but|otherwise)\b)", sentence)
        if part.strip()
    ]
    if len(clauses) > 1 and any(_matching_rules(clause) for clause in clauses):
        return clauses
    return [sentence]


def _matching_rules(sentence: str) -> list[tuple[str, str, str]]:
    lowered = sentence.lower()
    matches: list[tuple[str, str, str]] = []
    for focus, keywords, polarity, criterion in FOCUS_RULES:
        if any(keyword in lowered for keyword in keywords):
            matches.append((focus, polarity, criterion))
    return matches


def _provisional_attributes(focus: str, quote: str) -> dict[str, Any]:
    """Return draft-only Layer 2 inputs; replace with validated Pass B labels later."""

    lowered = quote.lower()
    named_agent = bool(re.search(r"\b(team|worker|office|school|government|woman|neighbour|they|he|she)\b", lowered))
    future_language = focus == "future_possibility" or bool(
        re.search(r"\b(will|hope|hopefully|plan|maybe|might)\b", lowered)
    )
    if focus == "benefactor":
        coping = "high"
    elif focus == "blocked_goal" and re.search(r"\b(still in the shelter|no right|cancelled)\b", lowered):
        coping = "low"
    else:
        coping = "zero" if re.search(r"\b(exhausted|no one can help|don't know who can help)\b", lowered) else "medium"

    if focus == "blocked_goal" and re.search(r"\b(cancelled|promised|had|was)\b", lowered):
        temporal = ["past"]
        if re.search(r"\b(still|are|now)\b", lowered):
            temporal.append("present")
    elif focus == "benefactor":
        temporal = ["present"]
    else:
        temporal = ["future"] if future_language else ["present"]

    return {
        "goal_relevance": RELEVANCE_BY_FOCUS[focus],
        "agency": ["other"] if named_agent else ["circumstance"],
        "certainty": ["uncertain"] if future_language else ["certain"],
        "temporal": temporal,
        "coping": coping,
        "norm_violation_level": 2 if re.search(r"\b(no right|shameless|wrong)\b", lowered) else 0,
        "self_blame_level": 2 if re.search(r"\b(my fault|blame myself|blamed myself)\b", lowered) else 0,
        "resource_depletion": bool(re.search(r"\b(exhausted|no energy|no one can help)\b", lowered)),
    }


def _scope_group(sentence: str, matches: list[tuple[str, str, str]]) -> str | None:
    """Group evidence-bearing sentences into native appraisal situations."""

    lowered = sentence.lower()
    if "neighbour says" in lowered or "neighbor says" in lowered:
        return None
    if any(match[0] == "benefactor" for match in matches):
        return "benefactor"
    if re.search(r"\b(office|flat|shelter|no right|cancelled|promised)\b", lowered):
        return "housing_obstacle"
    return matches[0][0] if matches else None


def pass_a_scope_lock(segment: Segment) -> dict[str, Any]:
    """Pass A: extract exact evidence and create ordered native scopes."""

    evidence: list[dict[str, str]] = []
    scopes: list[dict[str, Any]] = []
    scope_by_group: dict[str, dict[str, Any]] = {}
    for sentence in split_sentences(segment.respondent_answer):
        for unit in _evidence_units(sentence):
            matches = _matching_rules(unit)
            group = _scope_group(unit, matches)
            if group is None:
                continue
            evidence_id = f"e{len(evidence) + 1}"
            evidence.append({"id": evidence_id, "quote": unit})
            scope = scope_by_group.get(group)
            if scope is None:
                scope = {
                    "scope_id": f"s{len(scopes) + 1}",
                    "object": unit,
                    "stance_refs": [],
                    "context_items": [],
                    "relations_to_prior_scopes": [
                        {"scope_id": prior["scope_id"], "relation": "independent"}
                        for prior in scopes
                    ],
                }
                scopes.append(scope)
                scope_by_group[group] = scope
            scope["stance_refs"].append(evidence_id)
    return {"evidence": evidence, "scopes": scopes}


def pass_b_appraisal(scope_packet: dict[str, Any]) -> dict[str, Any]:
    """Pass B: annotate appraisal fields without changing locked scopes."""

    by_id = {item["id"]: item["quote"] for item in scope_packet["evidence"]}
    results: list[dict[str, Any]] = []
    for scope in scope_packet["scopes"]:
        quote = " ".join(by_id[ref] for ref in scope["stance_refs"])
        matches = _matching_rules(quote)
        focus, polarity, criterion = matches[0]
        results.append(
            {
                "scope_id": scope["scope_id"],
                "polarity": polarity,
                "focus": focus,
                "criterion": criterion,
                "support_refs": list(scope["stance_refs"]),
                "confidence": "medium",
                **_provisional_attributes(focus, quote),
            }
        )
    return {"scopes": results}

