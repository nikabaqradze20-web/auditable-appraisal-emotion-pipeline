"""Draft deterministic Layer 2 emotion scoring.

This module consumes validated Pass B appraisal scopes. It never reads the
original evidence text and never changes the appraisal interpretation. The
intensity modifiers and derived gates are provisional until checked against a
human-coded gold set.
"""

from __future__ import annotations

from typing import Any


CORE_MAP = {
    "threat": "anxiety_fear",
    "loss": "sadness_loss",
    "blocked_goal": "frustration",
    "dissatisfaction": "mild_negative",
    "felt_alleviation": "relief_safety",
    "benefactor": "gratitude",
    "future_possibility": "hope",
    "specific_object": "joy",
    "general_adequacy": "contentment",
}

FOCUS_ALIASES = {"mild_dissatisfaction": "dissatisfaction"}
NEGATIVE_EMOTIONS = {
    "anxiety_fear",
    "sadness_loss",
    "frustration",
    "mild_negative",
    "anger_indignation",
    "shame_guilt",
}
RELEVANCE_TO_INTENSITY = {"low": 1, "medium": 2, "high": 3}
INTENSITY_CAP = {"mild_negative": 1}
BLAME_AGENCY = {"other", "out_group", "in_group"}
SELF_AGENCY = {"self", "in_group"}


def gate_anger(scope: dict[str, Any]) -> bool:
    return (
        scope.get("norm_violation_level", 0) >= 2
        and bool(set(scope.get("agency", [])) & BLAME_AGENCY)
    )


def gate_shame(scope: dict[str, Any]) -> bool:
    return (
        scope.get("self_blame_level", 0) >= 2
        and bool(set(scope.get("agency", [])) & SELF_AGENCY)
    )


def scope_intensity(scope: dict[str, Any], emotion: str, errors: list[str]) -> int:
    relevance = scope.get("goal_relevance")
    if relevance not in RELEVANCE_TO_INTENSITY:
        errors.append(f"invalid_goal_relevance: {relevance!r}")
    value = RELEVANCE_TO_INTENSITY.get(relevance, 2)

    if scope.get("coping") == "zero" and emotion in NEGATIVE_EMOTIONS:
        value += 1
    if scope.get("resource_depletion") is True and emotion in NEGATIVE_EMOTIONS:
        value += 1

    value = max(1, min(value, 3))
    return min(value, INTENSITY_CAP.get(emotion, 3))


def score_scope(scope: dict[str, Any]) -> dict[str, Any]:
    """Score one Pass B scope and retain a human-readable decision trace."""

    emotions: dict[str, int] = {}
    trace: list[str] = []
    errors: list[str] = []
    scope_id = scope.get("scope_id")
    if not isinstance(scope_id, str) or not scope_id:
        errors.append("missing_scope_id")

    focus = FOCUS_ALIASES.get(scope.get("focus"), scope.get("focus"))
    core = CORE_MAP.get(focus)
    if core is None:
        errors.append(f"unknown_focus: {scope.get('focus')!r}")
    else:
        emotions[core] = scope_intensity(scope, core, errors)
        trace.append(f"focus={focus} -> {core}")

    if gate_anger(scope):
        emotions["anger_indignation"] = scope_intensity(scope, "anger_indignation", errors)
        trace.append("gate_anger fired")
    if gate_shame(scope):
        emotions["shame_guilt"] = scope_intensity(scope, "shame_guilt", errors)
        trace.append("gate_shame fired")

    return {"scope_id": scope_id, "emotions": emotions, "trace": trace, "errors": errors}


def score_segment(pass_b: dict[str, Any]) -> dict[str, Any]:
    """Score Pass B scopes independently, then merge labels by max intensity."""

    scopes = pass_b.get("scopes", [])
    if not scopes:
        return {"segment_emotions": {}, "per_scope": [], "errors": []}

    per_scope: list[dict[str, Any]] = []
    merged: dict[str, int] = {}
    errors: list[str] = []
    for scope in scopes:
        result = score_scope(scope)
        per_scope.append(result)
        errors.extend(result["errors"])
        for emotion, intensity in result["emotions"].items():
            merged[emotion] = max(merged.get(emotion, 0), intensity)

    return {"segment_emotions": merged, "per_scope": per_scope, "errors": errors}

