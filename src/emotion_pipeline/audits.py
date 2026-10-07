"""Blocking validators for each pipeline boundary.

Pass A and Pass B follow the blocking checks of the research run: structure,
verbatim evidence of 1 to 20 words, every evidence item assigned to exactly one
scope, scopes ordered by their first evidence item, and frozen scope identity in
Pass B. Allowed values per variable are enforced by the JSON Schemas in
``schemas/``. Layer 3 is checked against the fixed emotion map.
"""

from __future__ import annotations

from typing import Any

from .contracts import ContractError, Segment
from .emotion_scoring import EMOTION_MAP

MAX_QUOTE_WORDS = 20


def _audit(name: str, checks: list[tuple[str, bool]]) -> dict[str, Any]:
    issues = [message for message, passed in checks if not passed]
    return {"layer": name, "status": "pass" if not issues else "fail", "issues": issues}


def audit_pass_a(segment: Segment, packet: dict[str, Any]) -> dict[str, Any]:
    evidence = packet.get("evidence", [])
    scopes = packet.get("scopes", [])
    evidence_ids = [item.get("id") for item in evidence]
    position = {evidence_id: index for index, evidence_id in enumerate(evidence_ids)}
    refs = [ref for scope in scopes for ref in scope.get("evidence_refs", [])]
    first_refs = [position.get(scope["evidence_refs"][0], -1) for scope in scopes if scope.get("evidence_refs")]
    answer = segment.respondent_answer
    return _audit(
        "pass_a_scope_lock",
        [
            ("root keys are present", set(packet) == {"evidence", "scopes"}),
            ("evidence IDs are numbered in sequence", evidence_ids == [f"e{i}" for i in range(1, len(evidence_ids) + 1)]),
            ("every quote is verbatim source text", all(item.get("quote", "") in answer for item in evidence)),
            ("every quote has 1 to 20 words", all(1 <= len(item.get("quote", "").split()) <= MAX_QUOTE_WORDS for item in evidence)),
            ("scopes refer only to existing evidence", all(ref in position for ref in refs)),
            ("every evidence item belongs to exactly one scope", sorted(refs, key=str) == sorted(evidence_ids, key=str)),
            ("evidence is in text order within each scope", all(
                [position.get(ref, -1) for ref in scope.get("evidence_refs", [])]
                == sorted(position.get(ref, -1) for ref in scope.get("evidence_refs", []))
                for scope in scopes
            )),
            ("scopes are ordered by their first evidence item", first_refs == sorted(first_refs)),
        ],
    )


def audit_pass_b(scope_packet: dict[str, Any], appraisal_packet: dict[str, Any]) -> dict[str, Any]:
    scope_ids = [scope.get("scope_id") for scope in scope_packet.get("scopes", [])]
    appraisal_ids = [scope.get("scope_id") for scope in appraisal_packet.get("scopes", [])]
    return _audit(
        "pass_b_appraisal",
        [
            ("one record per frozen scope, same IDs, same order", scope_ids == appraisal_ids),
        ],
    )


def audit_layer3(appraisal_packet: dict[str, Any], emotion_packet: dict[str, Any]) -> dict[str, Any]:
    """Check Layer 3 against the fixed map: identity, primary emotion, anger rule."""

    records = appraisal_packet.get("scopes", [])
    derived = emotion_packet.get("per_scope", [])
    pairs = list(zip(records, derived))
    return _audit(
        "layer3_emotions",
        [
            ("scope identity is unchanged", [r.get("scope_id") for r in records] == [d.get("scope_id") for d in derived]),
            ("primary emotion follows the focus map", all(
                d.get("primary_emotion") == EMOTION_MAP.get(r.get("focus"), (None,))[0] for r, d in pairs
            )),
            ("anger only on negative scopes", all(
                "anger" not in d.get("overlays", []) or d.get("valence") == "negative" for d in derived
            )),
            ("no derivation errors are present", not emotion_packet.get("errors")),
        ],
    )


def assert_all_audits_pass(audits: list[dict[str, Any]]) -> None:
    failed = [audit for audit in audits if audit["status"] != "pass"]
    if failed:
        raise ContractError(f"failed audits: {failed}")
