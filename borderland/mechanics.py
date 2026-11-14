"""Public game mathematics. No world generator, random seed or answer keys here.

The reference solver may use these rules with facts it has legally inferred.
The simulator uses the same physical laws; tests also check independent fixtures.
"""

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product


MATRICES = (
    ((1, 1, 0), (0, 1, 1), (0, 0, 1)),
    ((1, 0, 1), (0, 1, 0), (0, 1, 1)),
)


def circuit(matrix, switches, phase):
    bias = (phase & 1, (phase >> 1) & 1, (phase & 1) ^ ((phase >> 1) & 1))
    return tuple((sum(a * x for a, x in zip(row, switches)) % 2) ^ b
                 for row, b in zip(matrix, bias))


def bid(mode, previous, offset, phase, round_index):
    if mode == "echo":
        return (previous + offset) % 21
    if mode == "mirror":
        return (20 - previous + offset) % 21
    return (3 * round_index + phase + offset) % 21


def balance_result(a, opponents, delta):
    target = (4 if delta == 1 else 3) * (a + sum(opponents)) // 15
    distances = [abs(v - target) for v in (a, *opponents)]
    return target, distances.count(min(distances)) == 1 and distances[0] == min(distances)


def balance_plan(mode, offsets, phase, delta):
    @lru_cache(None)
    def search(r, previous):
        if r == 3:
            return 0, ()
        choices = []
        for a in range(21):
            opponents = [bid(mode, previous, o, phase, r) for o in offsets[:2]]
            _, win = balance_result(a, opponents, delta)
            score, tail = search(r + 1, a)
            choices.append((int(win) + score, (a,) + tail))
        return max(choices, key=lambda c: (c[0], tuple(-v for v in c[1])))
    return search(0, 10)


@dataclass(frozen=True)
class ArenaState:
    apos: tuple
    ap: tuple
    bpos: tuple
    bp: tuple
    battery: int
    bb: tuple = (3, 3, 3)
    caches: int = 7
    raids: int = 0
    round: int = 1
    last_sector: int = 0
    collected: bool = False
    post_transfer: bool = False


class ArenaRules:
    """Immutable world facts supplied explicitly; state changes are pure."""

    def __init__(self, edges, sectors, phase, delta, mode, offsets, amendment,
                 caches=(2, 4, 6), abase=0, bbase=8, exit_node=5, exit_phases=(0, 1, 2, 3)):
        self.edges = {tuple(sorted((e["u"], e["v"]))): dict(e) for e in edges}
        self.sectors = tuple(sectors)
        self.phase, self.delta = phase, delta
        self.mode, self.offsets = mode, tuple(offsets)
        self.amendment = amendment
        self.cache_nodes = tuple(caches)
        self.abase, self.bbase, self.exit = abase, bbase, exit_node
        self.exit_phases = tuple(exit_phases)
        self.adj = {n: [] for n in range(9)}
        for u, v in self.edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        for n in self.adj:
            self.adj[n].sort()
        self._rival_cache = {}

    def open_edge(self, u, v, tick):
        edge = self.edges.get(tuple(sorted((u, v))))
        return bool(edge and (tick + self.phase) % 4 in edge["phases"]
                    and (not edge["powered"] or edge["indicator"] == self.delta))

    def power_cost(self, u, v):
        return int(self.edges[tuple(sorted((u, v)))]["powered"])

    def options(self, node, points, battery, round_index):
        if points <= 0:
            return (node,)
        return tuple([node] + [n for n in self.adj[node]
                              if self.open_edge(node, n, round_index)
                              and self.power_cost(node, n) <= battery])

    def rival_order(self, node, battery, target_sector, round_index):
        key = (node, battery, target_sector, round_index)
        if key in self._rival_cache:
            return self._rival_cache[key]
        queue = deque([(node, battery, (node,))])
        visited = {(node, battery)}
        candidates = []
        depth = None
        while queue:
            current, charge, path = queue.popleft()
            if depth is not None and len(path) > depth:
                break
            if self.sectors[current] == target_sector:
                depth = len(path)
                candidates.append((current, path))
                continue
            for neighbor in self.adj[current]:
                if not self.open_edge(current, neighbor, round_index):
                    continue
                left = charge - self.power_cost(current, neighbor)
                if left >= 0 and (neighbor, left) not in visited:
                    visited.add((neighbor, left))
                    queue.append((neighbor, left, path + (neighbor,)))
        if not candidates:
            result = node
        else:
            _, path = min(candidates)
            result = path[1] if len(path) > 1 else node
        self._rival_cache[key] = result
        return result

    def rival_orders(self, s):
        orders = []
        for j, (node, points, charge) in enumerate(zip(s.bpos, s.bp, s.bb)):
            if self.mode == "echo":
                target = (s.last_sector + self.offsets[j]) % 4
            elif self.mode == "mirror":
                target = (3 - s.last_sector + self.offsets[j]) % 4
            else:
                target = (s.round + self.phase + self.offsets[j]) % 4
            orders.append(self.rival_order(node, charge, target, s.round) if points else node)
        return tuple(orders)

    @staticmethod
    def transfer(points_from, from_ids, points_to, to_ids, amount):
        amount = min(amount, sum(points_from[i] for i in from_ids))
        remaining = amount
        for i in sorted(from_ids, key=lambda i: (-points_from[i], i)):
            debit = min(points_from[i], remaining)
            points_from[i] -= debit
            remaining -= debit
        receiver = min(to_ids, key=lambda i: (points_to[i], i))
        points_to[receiver] += amount
        return amount

    def advance(self, s, destinations):
        if s.round > 8:
            raise ValueError("arena already finished")
        if len(destinations) != 4:
            raise ValueError("four destinations required")
        rivals = self.rival_orders(s)  # computed BEFORE inspecting allied orders
        apos, bpos = list(s.apos), list(s.bpos)
        ap, bp, bb = list(s.ap), list(s.bp), list(s.bb)
        charge = s.battery
        eligible = []
        for i, dest in enumerate(destinations):
            if s.ap[i] and dest != s.apos[i] and self.open_edge(s.apos[i], dest, s.round):
                eligible.append((i, dest, self.power_cost(s.apos[i], dest)))
        total_cost = sum(c for _, _, c in eligible)
        for i, dest, cost in eligible:
            if cost and total_cost > s.battery:
                continue
            apos[i] = dest
            charge -= cost
        for j, dest in enumerate(rivals):
            if dest != bpos[j] and bp[j]:
                bb[j] -= self.power_cost(bpos[j], dest)
                bpos[j] = dest
        events = []
        polarity = self.delta if s.round < self.amendment else -self.delta
        post = s.post_transfer
        for node in range(9):
            ai = [i for i in range(4) if apos[i] == node and ap[i] > 0]
            bi = [i for i in range(3) if bpos[i] == node and bp[i] > 0]
            if not ai or not bi:
                continue
            at, bt = sum(ap[i] for i in ai), sum(bp[i] for i in bi)
            if at == bt:
                events.append({"kind": "encounter", "node": node, "transfer": 0, "allied": True})
                continue
            awin = (at > bt) if polarity == 1 else (at < bt)
            amount = self.transfer(bp, bi, ap, ai, 1000) if awin else self.transfer(ap, ai, bp, bi, 1000)
            signed = amount if awin else -amount
            events.append({"kind": "encounter", "node": node, "transfer": signed, "allied": True})
        if s.round >= self.amendment and sum(e["transfer"] for e in events) > 0:
            post = True
        caches, collected = s.caches, s.collected
        for c, node in enumerate(self.cache_nodes):
            if not caches & (1 << c):
                continue
            ai = [i for i in range(4) if apos[i] == node and ap[i] > 0]
            bi = [i for i in range(3) if bpos[i] == node and bp[i] > 0]
            if bool(ai) == bool(bi):
                continue
            points, ids = (ap, ai) if ai else (bp, bi)
            points[min(ids, key=lambda i: (points[i], i))] += 500
            caches &= ~(1 << c)
            collected |= bool(ai)
            events.append({"kind": "cache", "node": node, "allied": bool(ai), "points": 500})
        # Raids use a common snapshot and simultaneous deltas.
        raids, da, db = s.raids, [0] * 4, [0] * 3
        for bit, base, homepos, homep, enemypos, enemyp, hd, ed in (
            (0, self.abase, apos, ap, bpos, bp, da, db),
            (1, self.bbase, bpos, bp, apos, ap, db, da),
        ):
            enemies = [i for i in range(len(enemyp)) if enemypos[i] == base and enemyp[i] > 0]
            defended = any(p == base and q > 0 for p, q in zip(homepos, homep))
            homeids = [i for i, p in enumerate(homep) if p > 0]
            if not (raids & (1 << bit)) and enemies and not defended and homeids:
                hc, ec = list(homep), list(enemyp)
                amount = self.transfer(hc, homeids, ec, enemies, 1000)
                for i in range(len(hc)):
                    hd[i] += hc[i] - homep[i]
                for i in range(len(ec)):
                    ed[i] += ec[i] - enemyp[i]
                raids |= 1 << bit
                events.append({"kind": "raid", "node": base, "allied": True,
                               "transfer": amount if bit == 1 else -amount})
        ap = [p + d for p, d in zip(ap, da)]
        bp = [p + d for p, d in zip(bp, db)]
        last = s.last_sector
        events.sort(key=lambda e: (e["node"], {"encounter": 0, "cache": 1, "raid": 2}[e["kind"]]))
        for event in events:
            if event["allied"]:
                last = self.sectors[event["node"]]
        return ArenaState(tuple(apos), tuple(ap), tuple(bpos), tuple(bp), charge, tuple(bb),
                          caches, raids, s.round + 1, last, collected, post), events

    def won(self, s):
        return (s.round == 9 and sum(p > 0 for p in s.ap) >= 2
                and sum(s.ap) >= 11000 and sum(s.ap) > sum(s.bp)
                and any(n == self.exit and p > 0 for n, p in zip(s.apos, s.ap))
                and (8 + self.phase) % 4 in self.exit_phases
                and s.collected and s.post_transfer)

    def all_orders(self, s):
        return product(*(self.options(n, p, s.battery, s.round) for n, p in zip(s.apos, s.ap)))
