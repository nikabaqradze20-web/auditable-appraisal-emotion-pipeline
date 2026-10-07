import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from emotion_pipeline.audits import audit_pass_a, audit_pass_b
from emotion_pipeline.contracts import ContractError, Segment
from emotion_pipeline.emotion_mapping import derive_answer
from emotion_pipeline.pipeline import run_pipeline
from emotion_pipeline.schema_validation import validate_schema


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_segments.json"
TRACE_PATH = Path(__file__).resolve().parents[1] / "examples" / "SEG_SYN_001_trace.json"

BASE_RECORD = {
    "scope_id": "s1",
    "agency": ["other"],
    "temporal": ["present"],
    "certainty": ["certain"],
    "coping": "medium",
    "norm_violation_level": 0,
    "self_blame_level": 0,
    "resource_depletion": False,
    "goal_relevance": "medium",
}


def record(**changes):
    return dict(BASE_RECORD, **changes)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_all_synthetic_records_pass_every_validator(self):
        for item in self.records:
            result = run_pipeline(item)
            self.assertEqual(set(result["passes"]), {"pass_a_scope_lock", "pass_b_appraisal"})
            self.assertTrue(all(audit["status"] == "pass" for audit in result["audits"]))

    def test_pipeline_output_has_three_stages(self):
        result = run_pipeline(self.records[0])
        self.assertEqual(set(result), {"segment", "passes", "emotion_mapping", "audits"})

    def test_zero_scopes_is_a_coded_outcome(self):
        result = run_pipeline(self.records[-2])
        self.assertEqual(result["passes"]["pass_a_scope_lock"]["scopes"], [])
        self.assertEqual(result["passes"]["pass_b_appraisal"]["scopes"], [])
        self.assertEqual(result["emotion_mapping"]["answer_emotions"], [])

    def test_scope_identity_is_preserved_across_stages(self):
        result = run_pipeline(self.records[0])
        ids_a = [scope["scope_id"] for scope in result["passes"]["pass_a_scope_lock"]["scopes"]]
        ids_b = [scope["scope_id"] for scope in result["passes"]["pass_b_appraisal"]["scopes"]]
        ids_3 = [scope["scope_id"] for scope in result["emotion_mapping"]["per_scope"]]
        self.assertEqual(ids_a, ids_b)
        self.assertEqual(ids_a, ids_3)

    def test_non_synthetic_id_is_rejected(self):
        invalid = dict(self.records[0], segment_id="SEG_REAL_001")
        with self.assertRaises(ContractError):
            run_pipeline(invalid)

    def test_quotes_are_verbatim_evidence(self):
        result = run_pipeline(self.records[0])
        answer = self.records[0]["respondent_answer"]
        for item in result["passes"]["pass_a_scope_lock"]["evidence"]:
            self.assertIn(item["quote"], answer)

    def test_committed_trace_example_matches_the_pipeline(self):
        expected = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(run_pipeline(self.records[0]), expected)

    def test_canonical_example_emotions(self):
        mapping = run_pipeline(self.records[0])["emotion_mapping"]
        self.assertEqual(mapping["answer_emotions"], ["frustration", "anger", "gratitude"])
        self.assertEqual([scope["primary_emotion"] for scope in mapping["per_scope"]], ["frustration", "gratitude"])
        self.assertEqual(mapping["errors"], [])

    def test_every_focus_maps_to_one_primary_emotion(self):
        expected = {
            "threat": "fear_anxiety",
            "loss": "sadness",
            "blocked_goal": "frustration",
            "dissatisfaction": "discontent",
            "felt_alleviation": "relief",
            "benefactor": "gratitude",
            "future_possibility": "hope",
            "specific_object": "liking_enjoyment",
            "general_adequacy": "contentment",
        }
        for focus, emotion in expected.items():
            result = derive_answer({"scopes": [record(focus=focus)]})
            self.assertEqual(result["per_scope"][0]["primary_emotion"], emotion)
            self.assertEqual(result["answer_emotions"], [emotion])

    def test_anger_is_an_overlay_on_the_primary_emotion(self):
        result = derive_answer({"scopes": [record(focus="loss", agency=["out_group"], norm_violation_level=2)]})
        self.assertEqual(result["per_scope"][0]["primary_emotion"], "sadness")
        self.assertEqual(result["answer_emotions"], ["sadness", "anger"])

    def test_anger_needs_level_two_and_a_responsible_agent(self):
        below_threshold = derive_answer({"scopes": [record(focus="blocked_goal", norm_violation_level=1)]})
        impersonal = derive_answer({"scopes": [record(focus="blocked_goal", agency=["circumstance"], norm_violation_level=3)]})
        self.assertNotIn("anger", below_threshold["answer_emotions"])
        self.assertNotIn("anger", impersonal["answer_emotions"])

    def test_anger_never_fires_on_a_positive_scope(self):
        result = derive_answer({"scopes": [record(focus="benefactor", norm_violation_level=2)]})
        self.assertEqual(result["answer_emotions"], ["gratitude"])

    def test_self_blame_overlay_is_defined_but_not_analysed(self):
        result = derive_answer({"scopes": [record(focus="blocked_goal", agency=["self"], self_blame_level=2)]})
        self.assertTrue(result["per_scope"][0]["self_blame_overlay"])
        self.assertEqual(result["answer_emotions"], ["frustration"])

    def test_no_intensity_is_derived(self):
        result = derive_answer({"scopes": [record(focus="threat", goal_relevance="high", coping="zero")]})
        self.assertNotIn("intensity", json.dumps(result))
        self.assertEqual(result["answer_emotions"], ["fear_anxiety"])

    def test_answer_records_presence_not_counts(self):
        result = derive_answer({"scopes": [
            record(scope_id="s1", focus="blocked_goal"),
            record(scope_id="s2", focus="blocked_goal"),
            record(scope_id="s3", focus="threat"),
        ]})
        self.assertEqual(result["answer_emotions"], ["fear_anxiety", "frustration"])

    def test_pass_b_may_not_name_an_emotion(self):
        errors = validate_schema("pass_b_appraisal", {"scopes": [record(focus="threat", emotion="fear_anxiety")]})
        self.assertTrue(any("emotion" in error for error in errors))

    def test_pass_b_requires_all_nine_variables(self):
        incomplete = record(focus="threat")
        del incomplete["goal_relevance"]
        errors = validate_schema("pass_b_appraisal", {"scopes": [incomplete]})
        self.assertTrue(any("goal_relevance" in error for error in errors))

    def test_pass_b_may_not_change_scopes(self):
        audit = audit_pass_b(
            {"scopes": [{"scope_id": "s1"}, {"scope_id": "s2"}]},
            {"scopes": [record(scope_id="s1", focus="threat")]},
        )
        self.assertEqual(audit["status"], "fail")

    def test_pass_a_rejects_quotes_longer_than_twenty_words(self):
        answer = " ".join(f"word{i}" for i in range(25))
        segment = Segment("SEG_SYN_900", "Question?", answer)
        audit = audit_pass_a(segment, {"evidence": [{"id": "e1", "quote": answer}], "scopes": [{"scope_id": "s1", "evidence_refs": ["e1"]}]})
        self.assertIn("every quote has 1 to 20 words", audit["issues"])

    def test_pass_a_rejects_unassigned_evidence(self):
        segment = Segment("SEG_SYN_901", "Question?", "It is hard. It is fine.")
        audit = audit_pass_a(segment, {
            "evidence": [{"id": "e1", "quote": "It is hard"}, {"id": "e2", "quote": "It is fine"}],
            "scopes": [{"scope_id": "s1", "evidence_refs": ["e1"]}],
        })
        self.assertIn("every evidence item belongs to exactly one scope", audit["issues"])

    def test_evidence_extraction_is_not_tuned_to_canonical_quotes(self):
        alternate = {
            "segment_id": "SEG_SYN_007",
            "moderator_question": "What happened with the room?",
            "respondent_answer": "The office cancelled our room. They had no right, and we are still in the shelter.",
        }
        result = run_pipeline(alternate)
        quotes = [item["quote"] for item in result["passes"]["pass_a_scope_lock"]["evidence"]]
        self.assertEqual(quotes, [
            "The office cancelled our room",
            "They had no right",
            "we are still in the shelter",
        ])
        self.assertEqual(len(result["passes"]["pass_a_scope_lock"]["scopes"]), 1)


if __name__ == "__main__":
    unittest.main()
