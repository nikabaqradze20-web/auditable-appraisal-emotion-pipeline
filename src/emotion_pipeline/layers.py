"""Simple, deterministic implementations of Pass A and Pass B.

The functions are intentionally conservative. They are a runnable baseline for
testing scope and appraisal contracts, not a replacement for human annotation
or an LLM-based production annotator. Emotion scoring and segment aggregation
are intentionally not implemented yet.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import Segment


FOCUS_RULES: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("threat", ("worried", "afraid", "unsafe", "danger", "risk"), "negative", "possible harm is salient"),
    ("loss", ("lost", "gone", "missing"), "negative", "a valued object or condition is absent"),
    ("blocked_goal", ("cannot", "can't", "unable", "stuck", "delay", "no place"), "negative", "a desired outcome is obstructed"),
    ("dissatisfaction", ("disappointed", "frustrated", "unhappy", "terrible", "poor"), "negative", "the current outcome receives a negative verdict"),
    ("felt_alleviation", ("relieved", "relief", "burden lifted"), "positive", "an acute burden is described as ended"),
    ("benefactor", ("helped", "support", "grateful", "thank"), "positive", "another party provided valued help"),
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
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


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
    named_agent = bool(re.search(r"\b(team|worker|office|school|government|they|he|she)\b", lowered))
    future_language = focus == "future_possibility" or bool(
        re.search(r"\b(will|hope|hopefully|plan|maybe|might)\b", lowered)
    )
    return {
        "goal_relevance": RELEVANCE_BY_FOCUS[focus],
        "agency": ["other"] if named_agent else ["circumstance"],
        "certainty": ["uncertain"] if future_language else ["certain"],
        "temporal": ["future"] if future_language else ["present"],
        "coping": "zero" if re.search(r"\b(exhausted|no one can help|don't know who can help)\b", lowered) else "medium",
        "norm_violation_level": 2 if re.search(r"\b(no right|shameless|wrong)\b", lowered) else 0,
        "self_blame_level": 2 if re.search(r"\b(my fault|blame myself|blamed myself)\b", lowered) else 0,
        "resource_depletion": bool(re.search(r"\b(exhausted|no energy|no one can help)\b", lowered)),
    }


def pass_a_scope_lock(segment: Segment) -> dict[str, Any]:
    """Pass A: extract exact evidence and create ordered native scopes."""

    evidence: list[dict[str, str]] = []
    scopes: list[dict[str, Any]] = []
    for sentence in split_sentences(segment.respondent_answer):
        if not _matching_rules(sentence):
            continue
        evidence_id = f"e{len(evidence) + 1}"
        scope_id = f"s{len(scopes) + 1}"
        evidence.append({"id": evidence_id, "quote": sentence})
        scopes.append(
            {
                "scope_id": scope_id,
                "object": sentence[:80],
                "stance_refs": [evidence_id],
                "context_items": [],
                "relations_to_prior_scopes": [
                    {"scope_id": prior["scope_id"], "relation": "independent"}
                    for prior in scopes
                ],
            }
        )
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

