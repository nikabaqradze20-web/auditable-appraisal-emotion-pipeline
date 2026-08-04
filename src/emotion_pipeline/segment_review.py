"""Draft Layer 3 segment review and emotion aggregation."""

from __future__ import annotations

from typing import Any

from .contracts import Segment


NEGATIVE_EMOTIONS = {
    "anxiety_fear",
    "sadness_loss",
    "frustration",
    "mild_negative",
    "anger_indignation",
    "shame_guilt",
}
POSITIVE_EMOTIONS = {
    "relief_safety",
    "gratitude",
    "hope",
    "joy",
    "contentment",
}


def review_segment(segment: Segment, emotion_packet: dict[str, Any]) -> dict[str, Any]:
    """Review the complete Q+A and classify final valence and emotion presence."""

    final_emotions = list(emotion_packet.get("segment_emotions", {}))
    unresolved_errors = list(emotion_packet.get("errors", []))
    negative = bool(set(final_emotions) & NEGATIVE_EMOTIONS)
    positive = bool(set(final_emotions) & POSITIVE_EMOTIONS)

    if not final_emotions:
        valence = "neutral"
        emotion_present = "no"
        note = "No supported emotion was produced by Layer 2."
    elif negative and positive:
        valence = "mixed"
        emotion_present = "yes"
        note = "The segment contains both negative and positive validated emotions."
    elif negative:
        valence = "negative"
        emotion_present = "yes"
        note = "The segment contains validated negative emotions."
    else:
        valence = "positive"
        emotion_present = "yes"
        note = "The segment contains validated positive emotions."

    if unresolved_errors:
        note = "Layer 2 errors remain unresolved."

    return {
        "segment_id": segment.segment_id,
        "question": segment.moderator_question,
        "answer": segment.respondent_answer,
        "valence": valence,
        "emotion_present": emotion_present,
        "final_emotions": final_emotions,
        "review": {
            "clear": bool(
                segment.moderator_question.strip()
                and segment.respondent_answer.strip()
                and not unresolved_errors
            ),
            "ambiguity_flags": ["layer2_errors"] if unresolved_errors else [],
            "note": note,
        },
    }

