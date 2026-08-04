"""Orchestration for the implemented two-pass workflow."""

from __future__ import annotations

from typing import Any, Mapping

from .audits import (
    assert_all_audits_pass,
    audit_layer2,
    audit_layer3,
    audit_pass_a,
    audit_pass_b,
)
from .contracts import Segment
from .layers import (
    pass_a_scope_lock,
    pass_b_appraisal,
)
from .emotion_scoring import score_segment
from .segment_review import review_segment
from .schema_validation import assert_schema


def run_pipeline(value: Mapping[str, Any]) -> dict[str, Any]:
    assert_schema("segment", value)
    segment = Segment.from_mapping(value)

    pass_a = pass_a_scope_lock(segment)
    assert_schema("pass_a_scope_lock", pass_a)
    audit_a = audit_pass_a(segment, pass_a)
    assert_all_audits_pass([audit_a])

    pass_b = pass_b_appraisal(pass_a)
    assert_schema("pass_b_appraisal", pass_b)
    audit_b = audit_pass_b(pass_a, pass_b)
    emotions = score_segment(pass_b)
    assert_schema("layer2_emotions_draft", emotions)
    audit_emotions = audit_layer2(pass_b, emotions)
    segment_review = review_segment(segment, emotions)
    assert_schema("layer3_segment_review_draft", segment_review)
    audit_segment = audit_layer3(segment, segment_review)
    audits = [audit_a, audit_b, audit_emotions, audit_segment]
    assert_all_audits_pass(audits)

    return {
        "segment": {
            "segment_id": segment.segment_id,
            "moderator_question": segment.moderator_question,
            "respondent_answer": segment.respondent_answer,
        },
        "passes": {
            "pass_a_scope_lock": pass_a,
            "pass_b_appraisal": pass_b,
        },
        "layer2_emotions_draft": emotions,
        "layer3_segment_review_draft": segment_review,
        "audits": audits,
    }

