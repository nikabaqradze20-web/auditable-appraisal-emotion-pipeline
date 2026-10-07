"""Emotion mapping: deterministic emotion derivation in Python.

This module consumes validated Pass B records. It never reads the evidence text
and never changes an appraisal code. It follows the emotion map of the research
version:

- each focus category maps to exactly one primary emotion;
- anger is an overlay added to a negative scope when the respondent frames
  something as clearly wrong (norm violation >= 2) and a person, institution or
  group is responsible (agency includes other, out_group or in_group);
- a self-blame overlay is defined (self-blame level 2 plus self or in_group
  agency) but not analysed, because self-blame was not coded reliably;
- no intensity is derived;
- an answer carries an emotion when at least one of its scopes carries it.
"""

from __future__ import annotations

from typing import Any


# focus -> (primary emotion, valence, band)
EMOTION_MAP: dict[str, tuple[str, str, str]] = {
    "threat": ("fear_anxiety", "negative", "negative_threat"),
    "loss": ("sadness", "negative", "negative_loss"),
    "blocked_goal": ("frustration", "negative", "negative_obstruction"),
    "dissatisfaction": ("discontent", "negative", "negative_obstruction"),
    "felt_alleviation": ("relief", "positive", "positive_settled"),
    "benefactor": ("gratitude", "positive", "positive_active"),
    "future_possibility": ("hope", "positive", "positive_active"),
    "specific_object": ("liking_enjoyment", "positive", "positive_active"),
    "general_adequacy": ("contentment", "positive", "positive_settled"),
}

# Reporting order of the ten analysed emotions (nine primary emotions + anger).
EMOTION_ORDER = (
    "fear_anxiety",
    "sadness",
    "frustration",
    "discontent",
    "anger",
    "relief",
    "gratitude",
    "hope",
    "liking_enjoyment",
    "contentment",
)

ANGER_AGENCY = {"other", "out_group", "in_group"}
SELF_BLAME_AGENCY = {"self", "in_group"}


def anger_overlay(scope: dict[str, Any], valence: str | None) -> bool:
    return (
        valence == "negative"
        and scope.get("norm_violation_level", 0) >= 2
        and bool(set(scope.get("agency", [])) & ANGER_AGENCY)
    )


def self_blame_overlay(scope: dict[str, Any], valence: str | None) -> bool:
    """Defined as in the research version, but not analysed."""

    return (
        valence == "negative"
        and scope.get("self_blame_level", 0) >= 2
        and bool(set(scope.get("agency", [])) & SELF_BLAME_AGENCY)
    )


def derive_scope(scope: dict[str, Any]) -> dict[str, Any]:
    """Derive the primary emotion and overlays of one scope, with a trace."""

    errors: list[str] = []
    trace: list[str] = []
    scope_id = scope.get("scope_id")
    if not isinstance(scope_id, str) or not scope_id:
        errors.append("missing_scope_id")

    focus = scope.get("focus")
    mapped = EMOTION_MAP.get(focus)
    if mapped is None:
        errors.append(f"unknown_focus: {focus!r}")
        primary, valence, band = None, None, None
    else:
        primary, valence, band = mapped
        trace.append(f"focus={focus} -> {primary} ({valence}, {band})")

    overlays: list[str] = []
    if anger_overlay(scope, valence):
        overlays.append("anger")
        trace.append("anger overlay: negative scope, norm violation >= 2, other/out_group/in_group agency")

    self_blame = self_blame_overlay(scope, valence)
    if self_blame:
        trace.append("self-blame overlay fired (defined, not analysed)")

    return {
        "scope_id": scope_id,
        "primary_emotion": primary,
        "valence": valence,
        "band": band,
        "overlays": overlays,
        "self_blame_overlay": self_blame,
        "trace": trace,
        "errors": errors,
    }


def derive_answer(pass_b: dict[str, Any]) -> dict[str, Any]:
    """Derive emotions per scope, then record which emotions the answer carries."""

    per_scope = [derive_scope(scope) for scope in pass_b.get("scopes", [])]
    present: set[str] = set()
    errors: list[str] = []
    for result in per_scope:
        errors.extend(result["errors"])
        if result["primary_emotion"]:
            present.add(result["primary_emotion"])
        present.update(result["overlays"])

    return {
        "per_scope": per_scope,
        "answer_emotions": [emotion for emotion in EMOTION_ORDER if emotion in present],
        "errors": errors,
    }
