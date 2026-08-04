import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from emotion_pipeline.contracts import ContractError
from emotion_pipeline.pipeline import run_pipeline


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_segments.json"
TRACE_PATH = Path(__file__).resolve().parents[1] / "examples" / "SEG_SYN_001_trace.json"


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_all_synthetic_records_complete_both_passes(self):
        for record in self.records:
            result = run_pipeline(record)
            self.assertEqual(
                set(result["passes"]),
                {"pass_a_scope_lock", "pass_b_appraisal"},
            )
            self.assertTrue(all(audit["status"] == "pass" for audit in result["audits"]))
            self.assertIn("layer2_emotions_draft", result)

    def test_empty_appraisal_is_allowed(self):
        result = run_pipeline(self.records[-2])
        self.assertEqual(result["passes"]["pass_a_scope_lock"]["scopes"], [])
        self.assertEqual(result["passes"]["pass_b_appraisal"]["scopes"], [])
        self.assertEqual(result["layer2_emotions_draft"]["segment_emotions"], {})

    def test_scope_identity_is_preserved_across_layers(self):
        result = run_pipeline(self.records[0])
        scope_ids = [item["scope_id"] for item in result["passes"]["pass_a_scope_lock"]["scopes"]]
        appraisal_ids = [item["scope_id"] for item in result["passes"]["pass_b_appraisal"]["scopes"]]
        self.assertEqual(scope_ids, appraisal_ids)

    def test_non_synthetic_id_is_rejected(self):
        invalid = dict(self.records[0], segment_id="SEG_REAL_001")
        with self.assertRaises(ContractError):
            run_pipeline(invalid)

    def test_quotes_are_exact_evidence(self):
        result = run_pipeline(self.records[0])
        answer = self.records[0]["respondent_answer"]
        for item in result["passes"]["pass_a_scope_lock"]["evidence"]:
            self.assertIn(item["quote"], answer)

    def test_committed_trace_example_matches_the_pipeline(self):
        expected = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
        actual = run_pipeline(self.records[0])
        self.assertEqual(actual, expected)

    def test_layer2_maps_core_emotions_without_reinterpreting_scopes(self):
        result = run_pipeline(self.records[0])
        layer2 = result["layer2_emotions_draft"]
        self.assertEqual(
            layer2["segment_emotions"],
            {"anxiety_fear": 3, "relief_safety": 2},
        )
        self.assertEqual(
            [scope["scope_id"] for scope in layer2["per_scope"]],
            ["s1", "s2"],
        )
        self.assertEqual(layer2["errors"], [])

    def test_layer2_derived_gates_are_additive(self):
        from emotion_pipeline.emotion_scoring import score_segment

        result = score_segment(
            {
                "scopes": [
                    {
                        "scope_id": "s1",
                        "focus": "loss",
                        "goal_relevance": "high",
                        "agency": ["out_group"],
                        "norm_violation_level": 2,
                        "self_blame_level": 0,
                        "coping": "medium",
                        "resource_depletion": False,
                    }
                ]
            }
        )
        self.assertEqual(result["segment_emotions"], {"sadness_loss": 3, "anger_indignation": 3})

    def test_layer3_mixed_segment_keeps_frustration_and_hope(self):
        result = run_pipeline(self.records[-1])
        review = result["layer3_segment_review_draft"]
        self.assertEqual(review["valence"], "mixed")
        self.assertEqual(review["emotion_present"], "yes")
        self.assertEqual(review["final_emotions"], ["frustration", "hope"])

    def test_layer3_neutral_segment_returns_no_emotion(self):
        result = run_pipeline(self.records[-2])
        review = result["layer3_segment_review_draft"]
        self.assertEqual(review["valence"], "neutral")
        self.assertEqual(review["emotion_present"], "no")
        self.assertEqual(review["final_emotions"], [])


if __name__ == "__main__":
    unittest.main()

