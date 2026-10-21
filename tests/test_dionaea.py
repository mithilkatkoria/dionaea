import unittest
from dataclasses import replace
from dionaea.model import Scenario, make_stream
from dionaea.detectors import Settings, detect, METHODS
from dionaea.evaluate import evaluate, simulate
from dionaea.benchmark import candidates, choose_train_settings


class TestStream(unittest.TestCase):
    def test_reproducible(self):
        s = Scenario(seed=123)
        self.assertEqual(make_stream(s), make_stream(s))
        self.assertNotEqual(make_stream(s)["events"], make_stream(replace(s, seed=124))["events"])

    def test_valid_episode_intervals(self):
        s=make_stream(Scenario())
        for e in s["episodes"]:
            self.assertLess(e["start"], e["end"])
            self.assertTrue(all(s["truth"][e["start"]:e["end"]]))

    def test_bad_settings(self):
        with self.assertRaises(ValueError):
            make_stream(Scenario(noise=1.1))


class TestAlgorithms(unittest.TestCase):
    def test_single_event_and_cooldown(self):
        result=detect([1, 1, 1, 0, 1], "single", Settings(cooldown=2))
        self.assertEqual(result["alarms"], [0, 4])

    def test_pair_within_boundary(self):
        settings=Settings(window=3, cooldown=0)
        self.assertEqual(detect([1, 0, 0, 1], "pair", settings)["alarms"], [3])
        self.assertEqual(detect([1, 0, 0, 0, 1], "pair", settings)["alarms"], [])

    def test_count_based_detection(self):
        result=detect([1,0,1,0,1], "count", Settings(window=4,count=3,cooldown=0))
        self.assertEqual(result["alarms"], [4])

    def test_leaky_integrator(self):
        settings=Settings(alpha=.8,threshold=1.7,cooldown=0)
        self.assertEqual(detect([1,1,0], "leaky", settings)["alarms"], [1])
        self.assertEqual(detect([1,0,0,1], "leaky", settings)["alarms"], [])

    def test_causal_prefix(self):
        events=make_stream(Scenario(seed=33))["events"]
        for method in METHODS:
            prefix=detect(events[:180], method, Settings())
            full=detect(events, method, Settings())
            self.assertEqual(prefix["alarms"], [t for t in full["alarms"] if t<180])
            self.assertEqual(prefix["confidence"], full["confidence"][:180])

    def test_simulation_all_detectors(self):
        result=simulate(Scenario(seed=1),Settings())
        self.assertEqual(set(result["detectors"]),set(METHODS))
        self.assertEqual(len(result["events"]), 360)


class TestEvaluation(unittest.TestCase):
    def test_duplicate_alerts_are_false_positives(self):
        score=evaluate([11,12,45], [{"start":10,"end":15},{"start":30,"end":40}],100)
        self.assertEqual((score["tp"], score["fp"], score["fn"]),(1,2,1))
        self.assertEqual(score["mean_delay"],1)

    def test_no_predictions(self):
        s=evaluate([], [{"start":2,"end":5}],60)
        self.assertEqual((s["precision"],s["recall"],s["f1"]),(0,0,0))

    def test_training_determinism(self):
        streams=[make_stream(Scenario(seed=i)) for i in (10,11)]
        first=choose_train_settings("pair",streams)
        self.assertEqual(first,choose_train_settings("pair",streams))


if __name__ == "__main__":
    unittest.main()
