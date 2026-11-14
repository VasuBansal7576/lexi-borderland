"""Reference reasoning algorithms over public evidence. No private imports."""

from collections import deque
from heapq import heappop, heappush
from itertools import product

from mechanics import ArenaState


def timed_path(edges, start, targets, tick, battery, phase, delta, deadline=64):
    adj = {}
    for e in edges:
        if e["powered"] and e["indicator"] != delta:
            continue
        adj.setdefault(e["u"], []).append((e["v"], e))
        adj.setdefault(e["v"], []).append((e["u"], e))
    queue = [(0, tick, start, ())]
    best = {}
    while queue:
        spent, time, node, path = heappop(queue)
        key = (node, time % 4, spent)
        if time > deadline or time >= best.get(key, deadline + 1):
            continue
        best[key] = time
        if node in targets:
            return path
        for nxt, edge in sorted(adj.get(node, []), key=lambda pair: pair[0]):
            cost = int(edge["powered"])
            if spent + cost > battery:
                continue
            wait = next((dt for dt in range(4) if (time + dt + phase) % 4 in edge["phases"]), None)
            if wait is None:
                continue
            steps = (("wait", wait),) if wait else ()
            heappush(queue, (spent + cost, time + wait + edge["travel"], nxt,
                             path + steps + (("move", nxt),)))
    return None


def switch_path(start, target, forbidden=None):
    queue = deque([(tuple(start), ())])
    seen = {tuple(start)}
    while queue:
        state, path = queue.popleft()
        if state == tuple(target):
            return path
        for i in range(3):
            nxt = list(state)
            nxt[i] ^= 1
            nxt = tuple(nxt)
            if nxt == forbidden or nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + ((i, bool(nxt[i])),)))
    raise ValueError("no legal switch sequence inferred")


def arena_plan(rules, initial, width=96):
    """Bounded beam search finds a witness; failure is NOT an impossibility proof.

    The actual game retains all orders and point allocations. The reference
    planner tries several allocations; it never changes game rules to win.
    """
    allocations = [(2500, 2500, 2500, 2500), (7000, 1000, 1000, 1000),
                   (4000, 3000, 2000, 1000), (4900, 4900, 100, 100),
                   (100, 100, 4900, 4900), (8500, 500, 500, 500),
                   (4600, 1800, 1800, 1800), (1000, 2000, 3000, 4000)]
    distance = {rules.exit: 0}
    queue = deque([rules.exit])
    while queue:
        node = queue.popleft()
        for nxt in rules.adj[node]:
            if nxt not in distance:
                distance[nxt] = distance[node] + 1
                queue.append(nxt)
    def rank(s):
        own, rival = sum(s.ap), sum(s.bp)
        active = sum(v > 0 for v in s.ap)
        exit_distance = min((distance.get(n, 99) for n, p in zip(s.apos, s.ap) if p), default=99)
        # All quantities below derive from supplied evidence and public dynamics.
        return ((own - rival) / 1000 + 2 * s.collected + 3 * s.post_transfer
                + min(own, 11000) / 4000 + .2 * active + .08 * s.battery
                - (.2 if s.round < 6 else .8) * exit_distance)
    beam = []
    for allocation in allocations:
        s = ArenaState(initial.apos, allocation, initial.bpos, initial.bp, initial.battery)
        beam.append((s, allocation, ()))
    expanded = 0
    for depth in range(8):
        candidates = {}
        for state, allocation, path in beam:
            for orders in rules.all_orders(state):
                nxt, _ = rules.advance(state, orders)
                expanded += 1
                if sum(v > 0 for v in nxt.ap) < 2:
                    continue
                if min(distance.get(n, 99) for n, p in zip(nxt.apos, nxt.ap) if p) > 8 - depth - 1:
                    continue
                if depth == 7:
                    if rules.won(nxt):
                        return {"allocation": allocation, "orders": path + (orders,),
                                "final": nxt, "expanded": expanded, "width": width}
                    continue
                if nxt not in candidates:
                    candidates[nxt] = (allocation, path + (orders,))
        if not candidates:
            return None
        ranked = sorted(candidates, key=rank, reverse=True)
        # Keep breadth in positional configurations, rather than 96 near-clones.
        beam, buckets = [], {}
        for state in ranked:
            bucket = (tuple(sorted(state.apos)), state.collected, state.post_transfer, state.caches)
            if buckets.get(bucket, 0) >= 4:
                continue
            buckets[bucket] = buckets.get(bucket, 0) + 1
            allocation, path = candidates[state]
            beam.append((state, allocation, path))
            if len(beam) >= width:
                break
    return None
