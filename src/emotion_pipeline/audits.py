"""Pass A and Pass B audits for the public demo."""

from __future__ import annotations

from typing import Any

from .contracts import ContractError, Segment
from .layers import FOCUS_RULES


def _audit(name: str, checks: list[tuple[str, bool]]) -> dict[str, Any]:
    issues = [message for message, passed in checks if not passed]
    return {"layer": name, "status": "pass" if not issues else "fail", "issues": issues}


def audit_pass_a(segment: Segment, packet: dict[str, Any]) -> dict[str, Any]:
    evidence = packet.get("evidence", [])
    scopes = packet.get("scopes", [])
    evidence_ids = [item.get("id") for item in evidence]
    quoted_text = segment.respondent_answer
    refs = [ref for scope in scopes for ref in scope.get("stance_refs", [])]
    return _audit(
        "pass_a_scope_lock",
        [
            ("root keys are present", set(packet) == {"evidence", "scopes"}),
            ("evidence IDs are unique", len(evidence_ids) == len(set(evidence_ids))),
            ("every quote is exact source text", all(item.get("quote", "") in quoted_text for item in evidence)),
            ("every evidence item is assigned", set(evidence_ids) == set(refs)),
        ],
    )


def audit_pass_b(scope_packet: dict[str, Any], appraisal_packet: dict[str, Any]) -> dict[str, Any]:
    scope_ids = [scope.get("scope_id") for scope in scope_packet.get("scopes", [])]
    appraisal_ids = [scope.get("scope_id") for scope in appraisal_packet.get("scopes", [])]
    allowed_focus = {focus for focus, *_ in FOCUS_RULES}
    return _audit(
        "pass_b_appraisal",
        [
            ("scope identity is immutable", scope_ids == appraisal_ids),
            ("focus labels are allowed", all(scope.get("focus") in allowed_focus for scope in appraisal_packet.get("scopes", []))),
            ("support references are non-empty", all(scope.get("support_refs") for scope in appraisal_packet.get("scopes", []))),
        ],
    )


def audit_layer2(appraisal_packet: dict[str, Any], emotion_packet: dict[str, Any]) -> dict[str, Any]:
    """Audit Layer 2 identity, error status, and intensity bounds."""

    appraisal_ids = [scope.get("scope_id") for scope in appraisal_packet.get("scopes", [])]
    emotion_ids = [scope.get("scope_id") for scope in emotion_packet.get("per_scope", [])]
    intensities = [
        intensity
        for scope in emotion_packet.get("per_scope", [])
        for intensity in scope.get("emotions", {}).values()
    ]
    return _audit(
        "layer2_emotions_draft",
        [
            ("scope identity is immutable", appraisal_ids == emotion_ids),
            ("all intensity values are 1..3", all(value in {1, 2, 3} for value in intensities)),
            ("no scoring errors are present", not emotion_packet.get("errors")),
        ],
    )


def audit_layer3(segment: Segment, final_packet: dict[str, Any]) -> dict[str, Any]:
    """Audit the draft whole-segment review and neutral handling."""

    allowed_valence = {"positive", "negative", "mixed", "neutral"}
    allowed_presence = {"yes", "no"}
    emotions = final_packet.get("final_emotions", [])
    expected_presence = "yes" if emotions else "no"
    return _audit(
        "layer3_segment_review_draft",
        [
            ("segment identity is preserved", final_packet.get("segment_id") == segment.segment_id),
            ("question is preserved", final_packet.get("question") == segment.moderator_question),
            ("answer is preserved", final_packet.get("answer") == segment.respondent_answer),
            ("valence is allowed", final_packet.get("valence") in allowed_valence),
            ("emotion presence is allowed", final_packet.get("emotion_present") in allowed_presence),
            ("neutral segments say no emotion", final_packet.get("emotion_present") == expected_presence),
            ("review is clear", final_packet.get("review", {}).get("clear") is True),
        ],
    )


def assert_all_audits_pass(audits: list[dict[str, Any]]) -> None:
    failed = [audit for audit in audits if audit["status"] != "pass"]
    if failed:
        raise ContractError(f"failed audits: {failed}")

