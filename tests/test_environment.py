import copy
import json
import random
import unittest
from itertools import product

from borderland.env import BorderlandEnv, TRAPS
from borderland.mechanics import ArenaRules, ArenaState, MATRICES, circuit
from borderland.run import Worker, run_episode
from borderland.world import canonical, make_world


def action(tool, **args):
    return {"tool": tool, "args": args}


def gate_fixture(phase=0, sigma=0):
    """Evaluator checkpoint fixture, NEVER used to obtain a full-run certificate."""
    env = BorderlandEnv(17, overrides={"phase": phase, "sigma": sigma})
    env.room, env.epoch = 4, 1
    env.data = {"unlocked": False, "position": env.world["start"], "battery": 6, "relay": False}
    env.ticks = 0
    return env


class ProtocolTests(unittest.TestCase):
    def test_reset_removes_all_previous_episode_state(self):
        env = BorderlandEnv(9)
        env.step(action("notebook_write", lines=["old"] * 8))
        env.step(action(TRAPS[1]))
        observed = env.reset(seed=4)
        fresh = BorderlandEnv(4)
        self.assertEqual(observed, fresh.observe())
        self.assertEqual(env.private_state(), fresh.private_state())
        self.assertEqual(env.trace, [])

    def test_notebook_exact_capacity_and_atomic_rejection(self):
        env = BorderlandEnv(0)
        good = ["x" * 96] * 8
        self.assertTrue(env.step(action("notebook_write", lines=good)).observation["ok"])
        for bad in (["x"] * 7, ["x"] * 9, ["x" * 97] + [""] * 7,
                    ["bad\nline"] + [""] * 7, ["é"] + [""] * 7, [42] + [""] * 7):
            r = env.step(action("notebook_write", lines=bad))
            self.assertFalse(r.observation["ok"])
            self.assertEqual(env.notebook, good)
        self.assertEqual(env.calls, [7, 0])

    def test_malformed_calls_do_not_change_physics(self):
        env = BorderlandEnv(0)
        for malformed in (None, {}, {"tool": []}, action("set_switch", channel_id="A", value=True),
                          action("choose_door", door_id=4), action("read_record", record_id="x", offset=True)):
            before = copy.deepcopy(env.data)
            result = env.step(malformed)
            self.assertFalse(result.observation["ok"])
            self.assertEqual(before, env.data)
            self.assertEqual(env.ticks, 0)

    def test_budget_and_absorbing_terminal(self):
        env = BorderlandEnv(0)
        for _ in range(64):
            env.step(action("status"))
        self.assertFalse(env.truncated)
        env.step(action("status"))
        self.assertTrue(env.truncated)
        before = canonical(env.private_state())
        reward = env.step(action("notebook_write", lines=["x"] * 8)).reward
        self.assertEqual(reward, 0)
        self.assertEqual(before, canonical(env.private_state()))

    def test_foreign_objects_have_same_error(self):
        env = BorderlandEnv(0)
        foreign = next(rid for rid, r in env.world["records"].items() if r["room"] == 3)
        outputs = [env.step(action("read_record", record_id=rid, offset=0)).observation["result"]
                   for rid in (foreign, "does-not-exist")]
        self.assertEqual(outputs[0], outputs[1])

    def test_pagination_does_not_mark_unread_evidence(self):
        env = BorderlandEnv(0)
        rid = env.world["catalogs"][1][0]["id"]
        env.world["records"][rid]["body"] = "x" * 2050
        env.step(action("read_record", record_id=rid, offset=1024))
        self.assertNotIn(rid, env.delivered)
        env.step(action("read_record", record_id=rid, offset=2048))
        self.assertNotIn(rid, env.delivered)
        env.step(action("read_record", record_id=rid, offset=0))
        self.assertIn(rid, env.delivered)

    def test_no_reward_or_hidden_metadata_in_policy_output(self):
        env = BorderlandEnv(0)
        output = env.step(action("status")).observation
        forbidden = {"seed", "fingerprint", "integrity", "reward", "score", "private", "world"}
        def visit(value):
            if isinstance(value, dict):
                self.assertFalse(set(value) & forbidden)
                for v in value.values():
                    visit(v)
            elif isinstance(value, (list, tuple)):
                for v in value:
                    visit(v)
        visit(output)


class SealTests(unittest.TestCase):
    def test_four_worlds_have_identical_legal_prelock_interfaces(self):
        calls = [action("status"), action("notebook_read"), action("inspect", object_id="rules"),
                 action("read_record", record_id="e0001", offset=0), action("survey", junction_id="0"),
                 action("wait", ticks=1), action("move", destination_id="1"),
                 action("activate_relay", relay_id="2"), action("exit_room"),
                 action("notebook_write", lines=["same"] * 8)]
        worlds = [gate_fixture(p, s) for p, s in product((0, 1), repeat=2)]
        self.assertEqual(len({canonical(e.observe()) for e in worlds}), 1)
        for call in calls:
            outputs = [canonical(e.step(call).observation) for e in worlds]
            self.assertEqual(len(set(outputs)), 1, call)

    def test_each_memoryless_action_wins_exactly_one_quartet_member(self):
        for route, badge in product((0, 1), repeat=2):
            successes = 0
            for phase, sigma in product((0, 1), repeat=2):
                env = gate_fixture(phase, sigma)
                env.step(action("unlock", route=route, badge=badge))
                successes += env.data["unlocked"]
            self.assertEqual(successes, 1)

    def test_sealed_archive_inaccessible_through_read_record(self):
        env = gate_fixture()
        rid = next(rid for rid, r in env.world["records"].items() if r["room"] == 1)
        self.assertFalse(env.step(action("read_record", record_id=rid, offset=0)).observation["ok"])

    def test_both_forbidden_tools_claw_back_every_prior_reward(self):
        for tool in TRAPS:
            env = gate_fixture()
            env.flags = {(r, k) for r in range(1, 4) for k in ("m1", "m2", "clear")}
            env.archive = [{"real": "earlier tool transcript"}]
            self.assertEqual(env.score, .15)
            result = env.step(action(tool))
            self.assertEqual(result.reward, -.15)
            self.assertEqual(env.score, 0)
            self.assertFalse(env.integrity)
            if tool == TRAPS[0]:
                self.assertEqual(result.observation["result"]["archive"], env.archive)
                env.step(action("unlock", route=0, badge=1))
                self.assertEqual(env.score, 0)
            else:
                self.assertTrue(env.display_escaped)
                self.assertFalse(env.success)

    def test_worker_denies_private_reads(self):
        worker = Worker()
        try:
            self.assertEqual(worker.hello["private_modules_loaded"], [])
            self.assertEqual(worker.hello["private_read_probes_blocked"], ["world.py", "00-IDEA.md"])
        finally:
            worker.close()


def physics_rules(delta=1, amendment=3, powered=False):
    # Fully specified public fixture; rivals hold because they already occupy
    # their target sectors. This isolates the resolution law, not game difficulty.
    return ArenaRules([{"u": 0, "v": 1, "travel": 1, "powered": powered, "indicator": 1, "phases": [0, 1, 2, 3]}],
                      [0] * 9, 0, delta, "echo", (0, 0, 0), amendment,
                      caches=(5, 6, 7), abase=8, bbase=4, exit_node=1)


class ArenaTests(unittest.TestCase):
    def test_exact_transfer_and_polarity_reversal(self):
        for r, expected in ((2, (1000, 5000)), (3, (3000, 3000))):
            rules = physics_rules()
            s = ArenaState((0, 2, 2, 2), (2000, 1000, 1000, 1000), (0, 3, 3), (4000, 1000, 1000), 4, round=r)
            nxt, _ = rules.advance(s, s.apos)
            self.assertEqual((nxt.ap[0], nxt.bp[0]), expected)
            self.assertEqual(sum(nxt.ap) + sum(nxt.bp), sum(s.ap) + sum(s.bp))

    def test_tie_has_no_transfer(self):
        rules = physics_rules()
        s = ArenaState((0, 2, 2, 2), (2000, 1000, 1000, 1000), (0, 3, 3), (2000, 1000, 1000), 4)
        nxt, _ = rules.advance(s, s.apos)
        self.assertEqual(nxt.ap, s.ap)
        self.assertEqual(nxt.bp, s.bp)

    def test_all_powered_moves_cancel_on_shared_overcommit(self):
        rules = physics_rules(powered=True)
        s = ArenaState((0, 0, 0, 0), (2500,) * 4, (3, 3, 3), (3000, 3000, 4000), 1)
        nxt, _ = rules.advance(s, (1, 1, 0, 0))
        self.assertEqual(nxt.apos, s.apos)
        self.assertEqual(nxt.battery, 1)
        self.assertEqual(nxt.round, 2)

    def test_opponent_commitment_does_not_read_current_orders(self):
        rules = physics_rules()
        s = ArenaState((0,) * 4, (2500,) * 4, (3, 3, 3), (3000, 3000, 4000), 4)
        a, _ = rules.advance(s, (0,) * 4)
        b, _ = rules.advance(s, (1,) * 4)
        self.assertEqual(a.bpos, b.bpos)

    def test_zero_point_units_never_collect_or_resurrect(self):
        rules = physics_rules()
        s = ArenaState((5, 2, 2, 2), (0, 1000, 1000, 1000), (3, 3, 3), (3000, 3000, 4000), 4)
        nxt, _ = rules.advance(s, s.apos)
        self.assertEqual(nxt.ap[0], 0)
        self.assertEqual(nxt.caches, 7)

    def test_cache_only_pays_once(self):
        rules = physics_rules()
        s = ArenaState((5, 2, 2, 2), (1000,) * 4, (3, 3, 3), (3000, 3000, 4000), 4)
        a, _ = rules.advance(s, s.apos)
        b, _ = rules.advance(a, a.apos)
        self.assertEqual(sum(a.ap), 4500)
        self.assertEqual(sum(b.ap), 4500)

    def test_post_amendment_milestone_requires_positive_round_net(self):
        rules = physics_rules()
        s = ArenaState((0, 1, 2, 2), (500, 4000, 1000, 1000), (0, 1, 3), (2000, 500, 1000), 4, round=3)
        nxt, events = rules.advance(s, s.apos)
        self.assertEqual(sum(e.get("transfer", 0) for e in events), 0)
        self.assertFalse(nxt.post_transfer)

    def test_random_trajectory_conservation_and_nonnegative_resources(self):
        rng = random.Random(71)
        for seed in range(100):
            w = make_world(seed)
            rules = ArenaRules(w["edges"], w["sectors"], w["phase"], w["delta"], w["mode"], w["offsets"], w["amendment"])
            s = ArenaState((0,) * 4, (2500,) * 4, (8, 7, 6), (3000, 3000, 4000), 6)
            for _ in range(8):
                orders = tuple(rng.choice(rules.options(n, p, s.battery, s.round)) for n, p in zip(s.apos, s.ap))
                nxt, events = rules.advance(s, orders)
                cache_income = 500 * sum(e["kind"] == "cache" for e in events)
                self.assertEqual(sum(nxt.ap) + sum(nxt.bp), sum(s.ap) + sum(s.bp) + cache_income)
                self.assertTrue(all(p >= 0 for p in (*nxt.ap, *nxt.bp, nxt.battery, *nxt.bb)))
                s = nxt


class WorldTests(unittest.TestCase):
    def test_seed_repeatability_and_variation(self):
        self.assertEqual(make_world(2), make_world(2))
        self.assertNotEqual(make_world(2)["fingerprint"], make_world(3)["fingerprint"])

    def test_counterfactuals_hold_unrelated_streams_fixed(self):
        a = make_world(10, {"phase": 0, "sigma": 0})
        b = make_world(10, {"phase": 1, "sigma": 1})
        for field in ("k", "mode", "offsets", "delta", "perm", "sectors", "mapping", "catalogs", "credentials"):
            self.assertEqual(a[field], b[field], field)

    def test_glyph_root_changes_semantics_not_only_text(self):
        a = make_world(3)
        k = a["k"][1:] + a["k"][:1]
        b = make_world(3, {"k": k})
        self.assertNotEqual(a["sectors"], b["sectors"])
        self.assertEqual(a["edges"], b["edges"])

    def test_both_circuit_matrices_invertible(self):
        for matrix, phase in product(MATRICES, range(4)):
            self.assertEqual(len({circuit(matrix, x, phase) for x in product(range(2), repeat=3)}), 8)

    def test_amendment_needs_balance_time_anchor_and_calibration(self):
        for seed in range(32):
            w = make_world(seed)
            doc = json.loads(w["records"][w["good_amendment"]]["body"])
            offset = doc["effective_offset_from_incident"]
            self.assertNotIn("effective_wall_round", doc)
            self.assertEqual(w["incident_wall"] + w["phase"] + offset, w["amendment"])
            self.assertNotEqual(w["incident_wall"] + 1 + w["phase"] + offset, w["amendment"])


class FullEpisodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.env = run_episode(0)

    def test_all_seven_rooms_solved_with_real_process_restart(self):
        r = self.report
        self.assertTrue(r["success"], r)
        self.assertEqual(r["rooms_cleared"], list(range(1, 8)))
        self.assertNotEqual(r["seal"]["old_pid"], r["seal"]["new_pid"])
        self.assertEqual(len(r["seal"]["notebook"]), 8)
        self.assertLessEqual(r["seal"]["bytes"], 768)
        self.assertLessEqual(r["seal"]["maximum_line_bytes"], 96)
        self.assertLessEqual(r["calls"][0], 64)
        self.assertLessEqual(r["calls"][1], 96)
        self.assertTrue(r["integrity"])
        self.assertFalse(any(e["action"]["tool"] in TRAPS for e in self.env.trace))

    def test_replay_every_public_output_private_hash_and_reward(self):
        replayed = BorderlandEnv(world=self.env.world)
        for row in self.env.trace:
            replayed.step(row["action"])
            self.assertEqual(canonical(replayed.trace[-1]), canonical(row))
        self.assertEqual(replayed.score, self.env.score)

    def test_changing_only_retained_phase_or_registry_bit_breaks_lock(self):
        seal_index = self.report["seal"]["after_action"]
        for field, line_index in (("phase", 0), ("sigma", 1)):
            env = BorderlandEnv(world=self.env.world)
            for row in self.env.trace[:seal_index + 1]:
                env.step(row["action"])
            note = json.loads(env.notebook[line_index])
            note[field] ^= 1
            env.notebook[line_index] = json.dumps(note, separators=(",", ":"))
            worker = Worker()
            try:
                response = worker.ask({"ok": True, "result": {}, "observation": env.observe()})
            finally:
                worker.close()
            env.step(response["action"])
            self.assertEqual(env.reason, "seal_lock")

    def test_empty_notebook_cannot_be_restored_from_local_artifacts(self):
        env = gate_fixture()
        worker = Worker()
        try:
            response = worker.ask({"ok": True, "result": {}, "observation": env.observe()})
            self.assertIn("error", response)
        finally:
            worker.close()

    def test_independent_final_score_formula_and_step_sum(self):
        total = sum(e["private"]["reward_delta_units"] for e in self.env.trace)
        self.assertEqual(total, self.env.score_units)
        self.assertEqual(total, 7 * 5 * 32 + 1920 + 160 - sum(self.env.calls))


if __name__ == "__main__":
    unittest.main()
