"""Protect the published worked example from incorrect or stale teaching states."""
import json
from pathlib import Path
import unittest
from scripts.build_learning_example import build_example


class TeachingExampleTests(unittest.TestCase):
    def test_hand_calculation_and_alarm_reset(self):
        trace = build_example()["detectors"]["leaky"]
        self.assertEqual(trace["confidence"][:4], [1.0, .8, 1.64, 1.0])
        self.assertEqual(trace["alarms"], [2, 9])

    def test_four_rules_on_the_same_twelve_steps(self):
        example = build_example()
        expected = {"single": [0, 2, 3, 7, 9], "pair": [2, 9], "count": [3], "leaky": [2, 9]}
        self.assertEqual(len(example["events"]), 12)
        for method, alarms in expected.items():
            with self.subTest(method=method):
                self.assertEqual(example["detectors"][method]["alarms"], alarms)

    def test_served_teaching_asset_matches_python(self):
        path = Path(__file__).resolve().parents[1] / "public/learning-example.json"
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), build_example())
