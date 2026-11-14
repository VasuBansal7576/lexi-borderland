"""External spending guard; public data only, never a game rule or action mask."""
import copy
import json


def key(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def progress_state(observation):
    state = copy.deepcopy(observation)
    state.pop('notebook', None)  # rewriting notes alone must not evade the guard
    if state['room'] == 1:
        state.pop('clock', None)  # rule inspection increments this without revealing evidence
    return state


class LoopGuard:
    EVIDENCE_TOOLS = {'inspect', 'read_record', 'question', 'probe', 'survey', 'activate_relay'}

    def __init__(self, limit=3):
        self.limit = limit
        self.reset()

    def reset(self):
        self.seen_evidence = set()
        self.stagnant = 0

    def observe(self, before, action, after):
        changed = after['ok'] and progress_state(before['observation']) != progress_state(after['observation'])
        fresh = False
        if after['ok'] and action.get('tool') in self.EVIDENCE_TOOLS:
            # Changing reason text, IDs, or notebooks cannot manufacture new evidence.
            evidence = key(after['result'])
            fresh = evidence not in self.seen_evidence
            self.seen_evidence.add(evidence)
        if changed or fresh:
            self.stagnant = 0
        else:
            self.stagnant += 1
        return self.stagnant >= self.limit
