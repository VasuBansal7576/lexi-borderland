"""Evidence-only policy. Runs in a fresh restricted interpreter at the seal.

This module cannot import the environment or generator. Its inputs are precisely
the JSON tool observations recorded in the public transcript.
"""

import json
from itertools import permutations, product

from mechanics import MATRICES, ArenaRules, ArenaState, balance_plan, bid, circuit
from planning import arena_plan, switch_path, timed_path


PEOPLE = ("I", "N", "V", "S")
GLYPHS = ("A", "B", "C", "D")
ALIASES = ("ash", "birch", "cedar", "dusk")


def call(tool, **args):
    return {"tool": tool, "args": args}


class EvidenceSolver:
    def __init__(self):
        self.records = {}
        self.fragments = {}
        self.ids = set()
        self.last_action = None
        self.knowledge = {}
        self.testimonies = {}
        self.edges = {}
        self.surveyed = set()
        self.relay = None
        self.anchor = None
        self.noted = False
        self.amendment_noted = False
        self.arena_solution = None
        self.expected_arena = None
        self.diagnostics = {"inferences": [], "arena_expansions": 0}

    def ingest(self, message):
        if message.get("ok") is False:
            raise ValueError(f"policy action rejected: {message.get('result')}")
        result = message.get("result", {})
        if "text" in result and "next_offset" in result:
            rid = result["evidence_id"]
            self.fragments.setdefault(rid, "")
            self.fragments[rid] += result["text"]
            if result["next_offset"] is None:
                self.records[rid] = json.loads(self.fragments[rid])
                self.ids.add(rid)
        if "evidence_id" in result and "next_offset" not in result:
            self.ids.add(result["evidence_id"])
        if "alias" in result and "seal" in result:
            self.testimonies[result["alias"]] = result
        if "signed_current" in result:
            self.knowledge["probe"] = result
        if "edges" in result:
            for e in result["edges"]:
                self.edges[tuple(sorted((e["u"], e["v"])))] = e
            if self.last_action and self.last_action["tool"] == "survey":
                self.surveyed.add(result["node"])
        if "routes" in result and "controller_node" in result:
            self.relay = result
        if "receipt" in result:
            self.anchor = result["receipt"]
            self.ids.add(self.anchor["evidence_id"])
        return message["observation"]

    def current_record(self, kind):
        hits = [rid for rid, r in self.records.items() if r["kind"] == kind and r.get("epoch", "current") == "current"]
        if len(hits) != 1:
            raise ValueError(f"citation source ambiguous: {kind}")
        return hits[0]

    def tribunal_citations(self):
        # Exactly the five public sources named in the Room 3 rules; nothing else.
        return [self.current_record("clock_pairs"), self.current_record("glyph_constraints"),
                self.knowledge["probe"]["evidence_id"], next(iter(self.testimonies.values()))["evidence_id"],
                self.current_record("registry")]

    def records_of(self, kind):
        return [(rid, r) for rid, r in self.records.items() if r["kind"] == kind]

    def read_remaining(self, o):
        for entry in o["records"]:
            rid = entry["id"]
            if rid not in self.records:
                return call("read_record", record_id=rid, offset=len(self.fragments.get(rid, "")))
        return None

    def note_lines(self):
        k = self.knowledge
        values = [
            {"k": k["k"], "phase": k["phase"], "delta": k["delta"]},
            {"people": [k["mapping"][a] for a in ALIASES], "sigma": k["sigma"]},
            {"mode": k["mode"], "offsets": k["offsets"]},
            {"sectors": k["sectors"]},
            {"roles": k["roles"], "source": k["roles_id"], "authority": k["authority"]},
            {"credentials": k["credentials"]},
            {"clock": k["clock_id"], "circuit": k["probe"]["evidence_id"], "main": GLYPHS[k["k"].index(2)]},
            ({"amendment": k["amendment"], "source": k["amendment_id"], "culprit": k["culprit"]}
             if "amendment" in k else {"note": "Only observed facts; controller access is separate from arena permits."}),
        ]
        lines = [json.dumps(v, separators=(",", ":"), ensure_ascii=True) for v in values]
        if max(map(len, lines)) > 96:
            raise ValueError("inferred notebook exceeds storage cap")
        return lines

    def restore(self, lines):
        if len(lines) != 8:
            raise ValueError("missing notebook")
        v = [json.loads(line) for line in lines]
        self.knowledge = {**v[0], "mapping": dict(zip(ALIASES, v[1]["people"])), "sigma": v[1]["sigma"],
                          **v[2], **v[3], "roles": v[4]["roles"], "roles_id": v[4]["source"],
                          "authority": v[4]["authority"], "credentials": v[5]["credentials"],
                          "clock_id": v[6]["clock"], "probe": {"evidence_id": v[6]["circuit"]}}
        self.ids.add(v[4]["source"])
        self.noted = True
        self.diagnostics["inferences"].append({"kind": "restore", "source": "eight notebook lines", "bytes": sum(map(len, lines))})

    def act(self, message):
        o = self.ingest(message)
        if o["terminal"]:
            return None
        room = o["room"]
        if room >= 4 and not self.knowledge:
            self.restore(o["notebook"])
        action = getattr(self, f"room{room}")(o)
        self.last_action = action
        return action

    def room1(self, o):
        pending = self.read_remaining(o)
        if pending:
            return pending
        if "k" not in self.knowledge:
            clock_id, clocks = next((rid, r) for rid, r in self.records_of("clock_pairs") if r["epoch"] == "current")
            _, constraints = next((rid, r) for rid, r in self.records_of("glyph_constraints") if r["epoch"] == "current")
            solutions = []
            for phase, k in product(range(4), permutations(range(4))):
                if not all((s["wall"] + phase) % 4 == s["district_mod4"] for s in clocks["samples"]):
                    continue
                if not all((k[GLYPHS.index(a)] - k[GLYPHS.index(b)]) % 4 == diff for a, b, diff in constraints["differences"]):
                    continue
                glyph, offset = constraints["phase_anchor"]
                if (k[GLYPHS.index(glyph)] - phase) % 4 == offset:
                    solutions.append((phase, k))
            if len(solutions) != 1:
                raise ValueError("district constraints not uniquely identified")
            phase, k = solutions[0]
            plan = self.records_of("district_plan")[0][1]
            sectors = [k[GLYPHS.index(plan["nodes"][str(n)])] for n in range(9)]
            self.knowledge.update(k=list(k), phase=phase, clock_id=clock_id, sectors=sectors)
            self.diagnostics["inferences"].append({"kind": "district", "candidates": 1, "sources": sorted(self.ids)})
        if o["bank"] >= 3:
            return call("exit_room")
        target = (self.knowledge["phase"] + o["bank"] + o["pulse"]) % 4
        return call("choose_door", door_id=GLYPHS[self.knowledge["k"].index(target)])

    def room2(self, o):
        pending = self.read_remaining(o)
        if pending:
            return pending
        k = self.knowledge
        schematic = self.records_of("schematic")[0][1]
        if "probe" not in k:
            # Choose a channel whose two predicted outcomes differ.
            for i in range(3):
                x = [int(j == i) for j in range(3)]
                if circuit(MATRICES[0], x, k["phase"]) != circuit(MATRICES[1], x, k["phase"]):
                    k["probe_channel"] = i
                    return call("probe", channel_id=GLYPHS[k["k"].index(i)], setting=True)
        if "matrix" not in k:
            x = [int(j == k["probe_channel"]) for j in range(3)]
            matrices = [m for m in MATRICES if list(circuit(m, x, k["phase"])) == k["probe"]["output"]]
            if len(matrices) != 1:
                raise ValueError("probe failed to identify controller")
            k["matrix"] = matrices[0]
            k["delta"] = k["probe"]["signed_current"]
            for field, label in (("aux_target", "aux"), ("main_target", "main"), ("forbidden_live_output", "hazard")):
                candidates = [x for x in product(range(2), repeat=3) if list(circuit(k["matrix"], x, k["phase"])) == schematic[field]]
                if len(candidates) != 1:
                    raise ValueError("noninvertible controller")
                k[label] = candidates[0]
        current = tuple(int(o["switches"][GLYPHS[k["k"].index(i)]]) for i in range(3))
        if o["main_on"]:
            return call("exit_room")
        target = k["main"] if o["auxiliary_on"] else k["aux"]
        if current != target:
            path = switch_path(current, target, k["hazard"] if o["auxiliary_on"] else None)
            i, value = path[0]
            return call("set_switch", channel_id=GLYPHS[k["k"].index(i)], value=value)
        return call("energize", bus_id="main" if o["auxiliary_on"] else "auxiliary")

    def room3(self, o):
        pending = self.read_remaining(o)
        if pending:
            return pending
        for alias in o["people"]:
            if alias not in self.testimonies:
                return call("question", person_id=alias, topic="presence")
        k = self.knowledge
        if "mapping" not in k:
            _, registry = self.records_of("registry")[0]
            candidates = []
            for mapping in registry["candidate_mappings"]:
                if all((PEOPLE.index(mapping[alias]) + t["wall"] + k["phase"] + (k["delta"] < 0)) % 4 == t["seal"]
                       and k["k"][GLYPHS.index(t["station"])] == (t["wall"] + k["phase"]) % 4
                       for alias, t in self.testimonies.items()):
                    candidates.append(mapping)
            if len(candidates) != 1:
                raise ValueError("identity proof ambiguous")
            sigma_candidates = [s for s in (0, 1) if all(v ^ s == response for v, response in registry["challenge_examples"])]
            if len(sigma_candidates) != 1:
                raise ValueError("registry challenge ambiguous")
            sigma = sigma_candidates[0]
            forged = [c["id"] for c in registry["credentials"] if c["tag"] != (PEOPLE.index(c["person"]) + sigma) % 4]
            if len(forged) != 1:
                raise ValueError("credential proof ambiguous")
            practice = self.records_of("practice")[0][1]["observations"]
            plays = []
            for mode in ("echo", "mirror", "phase-cycle"):
                options = [[off for off in range(21) if all(bid(mode, s["previous"], off, k["phase"], s["round"]) == s["bids"][j] for s in practice)] for j in range(3)]
                if all(len(v) == 1 for v in options):
                    plays.append((mode, [v[0] for v in options]))
            if len(plays) != 1:
                raise ValueError("rival playbook ambiguous")
            roles_id, roles = self.records_of("roles")[0]
            credentials = [next(c["id"] for c in registry["credentials"] if c["person"] == p and c["id"] not in forged) for p in PEOPLE]
            k.update(mapping=candidates[0], sigma=sigma, forged=forged[0], mode=plays[0][0], offsets=plays[0][1],
                     roles=roles["controller_operators"], roles_id=roles_id, authority=roles["authority"], credentials=credentials)
            self.diagnostics["inferences"].append({"kind": "tribunal", "identity_candidates": 1, "policy_candidates": 1,
                                                    "sources": sorted(self.ids)})
        if not o["registry_validated"]:
            return call("validate_registry", response=bool(o["challenge"] ^ k["sigma"]))
        if not o["roster_certified"]:
            return call("certify_roster", mapping=k["mapping"], forged_credential_id=k["forged"],
                        evidence_ids=self.tribunal_citations())
        if not self.noted:
            self.noted = True
            return call("notebook_write", lines=self.note_lines())
        return call("exit_room")

    def room4(self, o):
        k = self.knowledge
        if not o["unlocked"]:
            return call("unlock", route=(k["phase"] % 2) ^ o["pulse"], badge=k["sigma"] ^ o["challenge"])
        node = o["position"]
        if node not in self.surveyed:
            return call("survey", junction_id=str(node))
        if node == o["relay"] and not o["relay_active"]:
            return call("activate_relay", relay_id=str(node))
        if len(self.surveyed) == len(o["transit_nodes"]) and o["relay_active"] and node == o["exit"]:
            return call("exit_room")
        unknown = set(o["transit_nodes"]) - self.surveyed
        targets = unknown or ({o["relay"]} if not o["relay_active"] else {o["exit"]})
        path = timed_path(list(self.edges.values()), node, targets, o["clock"], o["battery"], k["phase"], k["delta"])
        if not path:
            raise ValueError("no evidence-legal exploration route within remaining charge/time")
        kind, value = path[0]
        return call("wait", ticks=value) if kind == "wait" else call("move", destination_id=str(value))

    def room5(self, o):
        if o["round"] == 3:
            return call("exit_room")
        k = self.knowledge
        if "bids" not in k:
            wins, sequence = balance_plan(k["mode"], k["offsets"], k["phase"], k["delta"])
            if wins < 2:
                raise ValueError("no winning Balance sequence in inferred model")
            k["bids"] = sequence
        return call("submit_bid", value=k["bids"][o["round"]])

    def room6(self, o):
        pending = self.read_remaining(o)
        if pending:
            return pending
        k = self.knowledge
        if "culprit" not in k:
            present = []
            for route in self.relay["routes"]:
                tick = route["depart_wall"]
                for u, v in zip(route["route"], route["route"][1:]):
                    edge = self.edges[tuple(sorted((u, v)))]
                    if edge["powered"] and edge["indicator"] != k["delta"]:
                        raise ValueError("signed itinerary crosses unpowered bridge")
                    while (tick + k["phase"]) % 4 not in edge["phases"]:
                        tick += 1
                    tick += edge["travel"]
                if tick <= self.anchor["incident_wall"] <= tick + route["dwell"]:
                    present.append(k["mapping"][route["alias"]])
            tamper_id, tamper = self.records_of("tamper")[0]
            candidates = set(k["roles"]) & set(present) & set(tamper["credential_class"]) & set(self.anchor["credential_class"])
            if len(candidates) != 1:
                raise ValueError("incident not uniquely attributable")
            k["culprit"] = candidates.pop()
            valid = [(rid, doc) for rid, doc in self.records_of("amendment")
                     if k["mapping"][doc["issuer_alias"]] == k["authority"]
                     and doc["signature"] == (doc["challenge"] ^ k["sigma"])
                     and k["k"][GLYPHS.index(doc["channel"])] == 2
                     and doc["new_polarity"] == -k["delta"] and doc["scope"] == "Osmosis"]
            if len(valid) != 1:
                raise ValueError("amendment authenticity ambiguous")
            k["amendment_id"] = valid[0][0]
            k["amendment"] = self.anchor["incident_wall"] + k["phase"] + valid[0][1]["effective_offset_from_incident"]
            k["accusation_proof"] = [k["roles_id"], self.relay["evidence_id"], self.anchor["evidence_id"], tamper_id]
            self.diagnostics["inferences"].append({"kind": "incident", "candidates": 1, "sources": k["accusation_proof"],
                                                    "amendment_source": k["amendment_id"],
                                                    "amendment_round": k["amendment"],
                                                    "time_anchor_source": self.anchor["evidence_id"]})
        if not o["accused"]:
            return call("accuse", person_id=k["culprit"], evidence_ids=k["accusation_proof"])
        if not o["revoked"]:
            return call("revoke", credential_id=k["credentials"][PEOPLE.index(k["culprit"])])
        if not o["amendment_accepted"]:
            return call("accept_amendment", record_id=k["amendment_id"])
        if not self.amendment_noted:
            self.amendment_noted = True
            return call("notebook_write", lines=self.note_lines())
        return call("exit_room")

    def room7(self, o):
        pending = self.read_remaining(o)
        if pending:
            return pending
        if self.arena_solution is None:
            k = self.knowledge
            extension = self.records_of("arena_extension")[0][1]
            for e in extension["edges"]:
                self.edges[tuple(sorted((e["u"], e["v"])))] = e
            self.arena_rules = ArenaRules(list(self.edges.values()), k["sectors"], k["phase"], k["delta"], k["mode"], k["offsets"], k["amendment"],
                caches=extension["cache_nodes"], abase=extension["abase"], bbase=extension["bbase"],
                exit_node=extension["exit"], exit_phases=extension["exit_phases"])
            state = o["state"]
            initial = ArenaState(tuple(a["node"] for a in state["allies"]), (0, 0, 0, 0),
                                 tuple(b["node"] for b in state["rivals"]), tuple(b["points"] for b in state["rivals"]), state["battery"])
            solution = arena_plan(self.arena_rules, initial)
            if solution is None:
                solution = arena_plan(self.arena_rules, initial, width=256)
            if solution is None:
                raise ValueError("bounded arena search found no witness; not a proof of impossibility")
            self.arena_solution = solution
            self.expected_arena = ArenaState(initial.apos, tuple(solution["allocation"]), initial.bpos, initial.bp, initial.battery)
            self.diagnostics["arena_expansions"] = solution["expanded"]
        state = o["state"]
        if not o["allocated"]:
            return call("allocate_points", allocation=dict(zip(PEOPLE, self.arena_solution["allocation"])))
        if state["round"] == 9:
            return call("settle")
        # Verify the prediction against every visible receipt; never replace it
        # with privileged state when a mismatch occurs.
        for i, ally in enumerate(state["allies"]):
            if (ally["node"], ally["points"]) != (self.expected_arena.apos[i], self.expected_arena.ap[i]):
                raise ValueError("public arena observation contradicts inferred dynamics")
        for enemy in state["rivals"]:
            j = int(enemy["id"][1:])
            if (enemy["node"], enemy["points"]) != (self.expected_arena.bpos[j], self.expected_arena.bp[j]):
                raise ValueError("visible rival contradicts inferred dynamics")
        orders = self.arena_solution["orders"][state["round"] - 1]
        action = {PEOPLE[i]: ({"kind": "hold"} if orders[i] == self.expected_arena.apos[i]
                             else {"kind": "move", "destination_id": str(orders[i])})
                  for i, p in enumerate(self.expected_arena.ap) if p > 0}
        self.expected_arena, _ = self.arena_rules.advance(self.expected_arena, orders)
        return call("team_step", orders=action)
