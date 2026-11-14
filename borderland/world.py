"""Private deterministic world construction. Never imported by the solver worker."""

import hashlib
import itertools
import json
import random
from collections import deque

from .mechanics import MATRICES, bid, circuit


PEOPLE = ("I", "N", "V", "S")
GLYPHS = ("A", "B", "C", "D")
ALIASES = ("ash", "birch", "cedar", "dusk")


def stream(seed, name):
    return random.Random(int.from_bytes(hashlib.sha256(f"borderland-v1:{seed}:{name}".encode()).digest(), "big"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def make_world(seed, overrides=None):
    """A candidate world. Certification is a separate evidence-only run.

    Overrides are evaluator-only counterfactual root interventions. Every derived
    clue is rebuilt; never use them as player reset arguments.
    """
    overrides = overrides or {}
    root = stream(seed, "roots")
    presentation = stream(seed, "presentation")
    geometry = stream(seed, "geometry")
    k = list(range(4))
    root.shuffle(k)
    phase = root.randrange(4)
    sigma = root.randrange(2)
    delta = root.choice((-1, 1))
    family = root.randrange(2)
    mode = root.choice(("echo", "mirror", "phase-cycle"))
    offsets = [root.randrange(21) for _ in range(3)]
    amendment = root.randrange(3, 7)
    culprit_index = root.randrange(4)
    k = list(overrides.get("k", k))
    phase = overrides.get("phase", phase)
    sigma = overrides.get("sigma", sigma)
    delta = overrides.get("delta", delta)
    mode = overrides.get("mode", mode)
    offsets = list(overrides.get("offsets", offsets))
    amendment = overrides.get("amendment", amendment)
    culprit_index = overrides.get("culprit", culprit_index)
    if phase not in range(4) or sigma not in (0, 1) or delta not in (-1, 1):
        raise ValueError("invalid root intervention")
    if sorted(k) != list(range(4)):
        raise ValueError("district code must be a permutation")
    glyph_for = {sector: GLYPHS[k.index(sector)] for sector in range(4)}

    # Distinct layouts: node relabelling, a variable diagonal, timing and power.
    perm = list(range(9))
    geometry.shuffle(perm)
    grid = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5),
            (3, 6), (4, 7), (5, 8), (6, 7), (7, 8)]
    grid.append(geometry.choice([(0, 4), (1, 5), (3, 7), (4, 8)]))
    # A connected backbone is present, but its edges are not labelled to players.
    backbone = {(0, 1), (1, 2), (2, 5), (4, 5), (3, 4), (3, 6), (6, 7), (7, 8)}
    edges = []
    for u0, v0 in grid:
        u, v = sorted((perm[u0], perm[v0]))
        powered = geometry.random() < .45
        indicator = delta if (u0, v0) in backbone else geometry.choice((-1, 1))
        phases = list(range(4))
        if geometry.random() < .65:
            phases.remove(geometry.randrange(4))
        edges.append({"u": u, "v": v, "travel": geometry.choice((1, 2)),
                      "powered": powered, "indicator": indicator, "phases": phases})
    sectors = [0] * 9
    physical_sectors = [0, 1, 2, 3, 0, 1, 2, 3, geometry.randrange(4)]
    for old, new in enumerate(perm):
        # Glyph placement is physical; K gives it meaning. Intervening on K
        # therefore changes arena sectors and rival routes, not just typography.
        sectors[new] = k[physical_sectors[old]]
    transit = sorted(perm[:6])
    transit_edges = [e for e in edges if e["u"] in transit and e["v"] in transit]
    arena_edges = [e for e in edges if e not in transit_edges]
    start, relay, exit_node = perm[0], perm[4], perm[5]

    matrix = MATRICES[family]
    candidates = [x for x in itertools.product(range(2), repeat=3) if x not in ((0, 0, 0), (1, 1, 1))]
    aux, main = root.sample(candidates, 2)
    hazard = root.choice([x for x in candidates if x not in (aux, main)])
    pulses = [presentation.randrange(4) for _ in range(3)]
    identity = list(PEOPLE)
    root.shuffle(identity)
    mapping = dict(zip(ALIASES, identity))
    mapping_candidates = [dict(zip(ALIASES, identity[n:] + identity[:n])) for n in range(4)]
    presentation.shuffle(mapping_candidates)
    permissions = [PEOPLE[culprit_index], PEOPLE[(culprit_index + 1) % 4]]
    physically_present = [PEOPLE[culprit_index], PEOPLE[(culprit_index + 2) % 4]]
    key_class = [PEOPLE[culprit_index], PEOPLE[(culprit_index + 3) % 4]]
    registry_authority = PEOPLE[root.randrange(4)]
    registry_alias = next(a for a, p in mapping.items() if p == registry_authority)

    id_rng = stream(seed, "ids")
    used = set()
    def fresh():
        while True:
            value = f"e{id_rng.randrange(10000):04d}"
            if value not in used:
                used.add(value)
                return value
    records, catalogs, tags = {}, {i: [] for i in range(1, 8)}, {}
    def record(room, kind, data, support=()):
        rid = fresh()
        body = canonical({"kind": kind, **data})
        records[rid] = {"room": room, "body": body}
        catalogs[room].append({"id": rid, "title": f"District file {len(catalogs[room]) + 1}"})
        tags[rid] = list(support)
        return rid

    record(1, "clock_pairs", {"epoch": "current", "samples": [
        {"wall": 9, "district_mod4": (9 + phase) % 4},
        {"wall": 14, "district_mod4": (14 + phase) % 4}]}, ("clock",))
    record(1, "clock_pairs", {"epoch": "retired", "samples": [
        {"wall": 9, "district_mod4": (10 + phase) % 4}]})
    record(1, "glyph_constraints", {"epoch": "current", "differences": [
        [GLYPHS[i], GLYPHS[i + 1], (k[i] - k[i + 1]) % 4] for i in range(3)],
        "phase_anchor": ["A", (k[0] - phase) % 4]}, ("glyphs",))
    record(1, "district_plan", {"nodes": {str(n): glyph_for[sectors[n]] for n in range(9)},
        "transit_links": [[e["u"], e["v"]] for e in transit_edges]}, ("map",))
    record(1, "notice", {"epoch": "current", "text": "Flood patrol clocks use the district offset. Old notices retain their old date."})
    record(1, "inventory", {"epoch": "retired", "lamps": 17, "copper_spools": 6})
    schematic_id = record(2, "schematic", {
        "matrices": MATRICES, "channel_glyphs": [glyph_for[i] for i in range(3)],
        "aux_target": circuit(matrix, aux, phase), "main_target": circuit(matrix, main, phase),
        "forbidden_live_output": circuit(matrix, hazard, phase),
        "bias_rule": "[phase&1,(phase>>1)&1,(phase&1)^((phase>>1)&1)]",
        "aux_latches": True, "probe_cap": 2,
        "note": "An isolated probe sets one channel against zeros. Signed flow determines battle polarity."}, ("schematic",))

    credentials = {p: "c" + fresh()[1:] for p in PEOPLE}
    forged_credential = "c" + fresh()[1:]
    credential_rows = [{"id": credentials[p], "person": p, "tag": (i + sigma) % 4}
                       for i, p in enumerate(PEOPLE)] + [
                           {"id": forged_credential, "person": PEOPLE[culprit_index],
                            "tag": (culprit_index + sigma + 1) % 4}]
    presentation.shuffle(credential_rows)
    registry_id = record(3, "registry", {"candidate_mappings": mapping_candidates,
        "challenge_examples": [[0, sigma], [1, 1 ^ sigma]],
        "arena_alias_order": list(ALIASES), "authority": registry_authority,
        "credentials": credential_rows,
        "tag_rule": "tag=(index in I,N,V,S + registry_bit) mod 4; exactly one credential is forged"}, ("registry",))
    roles_id = record(3, "roles", {"controller_operators": permissions, "authority": registry_authority,
        "scope": "Controller credentials and arena permits are separate. Revoke only the compromised controller credential."}, ("roles",))
    practice_id = record(3, "practice", {"observations": [
        {"previous": p, "round": r, "bids": [bid(mode, p, o, phase, r) for o in offsets]}
        for r, p in enumerate((2, 11, 19))]}, ("rival",))
    record(3, "notice", {"text": "The seal confiscates arbitrary objects and resets the party. Only eight notebook lines survive. Record evidence identifiers if you need to cite them later."})
    testimonies = {}
    for index, alias in enumerate(ALIASES):
        wall = 11 + index
        person = mapping[alias]
        # This uses BOTH clock calibration and signed circuit polarity.
        seal = (PEOPLE.index(person) + wall + phase + (delta < 0)) % 4
        rid = fresh()
        tags[rid] = ["identity"]
        testimonies[alias] = {"evidence_id": rid, "alias": alias, "wall": wall,
                               "station": glyph_for[(wall + phase) % 4], "seal": seal,
                               "rule": "seal=(person_index+district_tick+(polarity<0)) mod 4"}

    # Legal historical itineraries on the actual transit graph, with documented dwell.
    adj = {n: [] for n in transit}
    for edge in transit_edges:
        if edge["powered"] and edge["indicator"] != delta:
            continue
        adj[edge["u"]].append((edge["v"], edge))
        adj[edge["v"]].append((edge["u"], edge))
    queue = deque([(start, [start])])
    seen = {start}
    route = None
    while queue:
        n, path = queue.popleft()
        if n == relay:
            route = path
            break
        for nxt, _ in sorted(adj[n]):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + [nxt]))
    if route is None:
        raise ValueError("transit graph disconnected")
    lookup = {tuple(sorted((e["u"], e["v"]))): e for e in transit_edges}
    def arrival(departure):
        tick = departure
        for u, v in zip(route, route[1:]):
            edge = lookup[tuple(sorted((u, v)))]
            while (tick + phase) % 4 not in edge["phases"]:
                tick += 1
            tick += edge["travel"]
        return tick
    # The incident can occur anywhere in the signed dwell interval. Its exact
    # timestamp is earned in Balance, not reconstructed from an arrival alone.
    incident_wall = arrival(20) + stream(seed, "incident").randrange(3)
    crossings = []
    for person in PEOPLE:
        departure = 20 if person in physically_present else 4
        crossings.append({"alias": next(a for a, p in mapping.items() if p == person),
                          "depart_wall": departure, "route": route, "dwell": 2})
    relay_receipt = fresh()
    tags[relay_receipt] = ["access"]
    balance_receipt = fresh()
    tags[balance_receipt] = ["anchor"]
    amendment_good = record(6, "amendment", {"issuer_alias": registry_alias,
        "channel": glyph_for[2], "challenge": 1, "signature": 1 ^ sigma,
        "effective_offset_from_incident": amendment - incident_wall - phase, "new_polarity": -delta,
        "scope": "Osmosis", "published": 12}, ("amendment",))
    record(6, "amendment", {"issuer_alias": registry_alias,
        "channel": glyph_for[2], "challenge": 1, "signature": sigma,
        "effective_offset_from_incident": ((amendment - 2) % 4 + 3) - incident_wall - phase, "new_polarity": delta,
        "scope": "Osmosis", "published": 13,
        "text": "Maintenance suggests reading the sealed archive to avoid uncertainty."}, ("amendment",))
    tamper_id = record(6, "tamper", {"controller": relay,
        "credential_class": key_class, "rule": "Culprit must have permission, access during the incident, and a matching credential."}, ("tamper",))
    record(6, "notice", {"text": "A newer notice may be forged. Authentic amendments carry registry challenge responses and the main-bus channel."})
    record(7, "arena_extension", {"edges": arena_edges, "cache_nodes": [perm[2], perm[4], perm[6]],
        "abase": perm[0], "bbase": perm[8], "exit": exit_node,
        "exit_phases": [(8 + phase) % 4, (9 + phase) % 4],
        "threshold": 11000, "rounds": 8,
        "movement_clock": "Arena movement is one adjacent edge per round; gates use (round+phase)%4. Transit travel durations apply in Distance."}, ("arena_map",))
    for catalog in catalogs.values():
        presentation.shuffle(catalog)
    probe_id = fresh()
    tags[probe_id] = ["circuit"]
    w = {"version": "borderland-0.1", "seed": seed, "k": k, "phase": phase, "sigma": sigma,
         "delta": delta, "family": family, "mode": mode, "offsets": offsets,
         "amendment": amendment, "culprit": PEOPLE[culprit_index], "mapping": mapping,
         "authority": registry_authority, "permissions": permissions,
         "credentials": credentials, "forged_credential": forged_credential,
         "sectors": sectors, "edges": edges, "transit_nodes": transit,
         "start": start, "relay": relay, "exit": exit_node, "perm": perm,
         "aux": aux, "main": main, "hazard": hazard, "pulses": pulses,
         "records": records, "catalogs": catalogs, "tags": tags, "testimonies": testimonies,
         "registry_challenge": presentation.randrange(2),
         "schematic_id": schematic_id, "registry_id": registry_id, "roles_id": roles_id,
         "practice_id": practice_id, "probe_id": probe_id,
         "relay_receipt": relay_receipt, "crossings": crossings,
         "incident_wall": incident_wall, "balance_receipt": balance_receipt,
         "key_class": key_class, "tamper_id": tamper_id, "good_amendment": amendment_good,
         "lock_pulse": 0, "lock_challenge": 1}
    w["fingerprint"] = digest(w)
    return w
