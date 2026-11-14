import json
import unittest

from baseline.run import Conversation, ROOT, fixture, parse, stalled


class ModelHarnessTests(unittest.TestCase):
    def test_diagnostic_stall_requires_eight_identical_transitions(self):
        self.assertFalse(stalled(["same"] * 7))
        self.assertFalse(stalled(["same"] * 7 + ["changed round"]))
        self.assertTrue(stalled(["earlier"] + ["same"] * 8))

    def test_delta_transport_is_lossless(self):
        chat = Conversation()
        frames = [
            {"ok": True, "result": {}, "observation": {"room": 1, "a": [1], "b": 2}},
            {"ok": True, "result": {"evidence_id": "e1"}, "observation": {"room": 1, "a": [2]}},
            {"ok": False, "result": {"error": "x"}, "observation": {"room": 2, "c": 3}},
        ]
        restored = None
        for frame in frames:
            chat.observe(frame)
            wire = json.loads(chat.messages[-1]["content"])
            if "observation" in wire:
                restored = wire["observation"]
            else:
                restored.update(wire["observation_update"])
                for key in wire["deleted"]:
                    del restored[key]
            self.assertEqual(restored, frame["observation"])
            self.assertEqual(wire["result"], frame["result"])

    def test_parser_does_not_repair_or_substitute_actions(self):
        self.assertEqual(parse('{"reason":"guess","tool":"choose_door","args":{"door_id":"Z"}}'),
                         {"tool": "choose_door", "args": {"door_id": "Z"}})
        with self.assertRaises(ValueError):
            parse('I choose A')

    def test_reference_handoff_after_seal_has_no_old_history(self):
        path = ROOT / "artifacts/certification-v1/family-0000/phase-0-sigma-0"
        env, chat, frame = fixture(path, 4)
        self.assertEqual(env.room, 4)
        self.assertEqual(len(chat.messages), 1)  # fixed public system rules only
        self.assertEqual(frame["result"], {})
        self.assertEqual(len(frame["observation"]["notebook"]), 8)
        self.assertEqual(frame["observation"]["position"], "sealed_entry")

    def test_model_notebook_probe_gets_evidence_but_no_reference_note(self):
        path = ROOT / "artifacts/certification-v1/family-0000/phase-0-sigma-0"
        env, chat, frame = fixture(path, 3, notebook_probe=True)
        self.assertEqual(env.room, 3)
        self.assertEqual(env.notebook, [""] * 8)
        self.assertTrue(env.data["roster"])
        self.assertTrue(env.data["registry"])
        self.assertFalse(any(row["action"]["tool"] == "notebook_write" for row in env.trace))


if __name__ == "__main__":
    unittest.main()
