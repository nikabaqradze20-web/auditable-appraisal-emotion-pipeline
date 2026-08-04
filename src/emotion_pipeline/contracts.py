"""Small contracts shared by the deterministic demo pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when a layer output violates its public contract."""


@dataclass(frozen=True)
class Segment:
    segment_id: str
    moderator_question: str
    respondent_answer: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Segment":
        required = {"segment_id", "moderator_question", "respondent_answer"}
        missing = sorted(required - set(value))
        if missing:
            raise ContractError(f"segment is missing fields: {missing}")
        segment_id = str(value["segment_id"])
        question = str(value["moderator_question"])
        answer = str(value["respondent_answer"])
        if not segment_id.startswith("SEG_SYN_"):
            raise ContractError("public fixtures must use synthetic SEG_SYN_ IDs")
        if not question.strip() or not answer.strip():
            raise ContractError("question and answer must be non-empty")
        return cls(segment_id, question, answer)

