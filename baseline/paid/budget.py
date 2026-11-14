"""Durable, single-flight reservations. Unknown charges never silently disappear."""
from decimal import Decimal
import fcntl
import hashlib
import json
import os
import threading
from functools import wraps
from .config import local_path


class BudgetStop(RuntimeError):
    pass


def persist(path, state):
    temp = local_path(path.with_name(path.name + '.tmp'))
    with temp.open('w') as handle:
        json.dump(state, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    os.replace(str(temp), str(path))
    directory = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def synchronized(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        with self.thread_lock:
            if self.lock.closed:
                raise BudgetStop('ledger_closed')
            return method(self, *args, **kwargs)
    return wrapped


class Ledger:
    def __init__(self, config, path):
        self.thread_lock = threading.RLock()
        self.config, self.path = config, local_path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = local_path(self.path.with_name(self.path.name + '.lock')).open('a+')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lock.close()
            raise BudgetStop('ledger_in_use') from None
        try:
            contract = config.contract()
            digest = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
            if self.path.exists():
                self.state = json.loads(self.path.read_text())
                if self.state.get('contract_hash') != digest:
                    raise BudgetStop('ledger_config_mismatch')
                self._validate_loaded()
            else:
                self.state = {'version': 1, 'contract_hash': digest, 'contract': contract, 'calls': 0,
                              'input_tokens_accounted': 0, 'output_tokens_accounted': 0,
                              'cost_accounted_usd': '0', 'pending': None, 'halted': None, 'entries': []}
                self.save()
        except BaseException:
            self.close()
            raise

    def _validate_loaded(self):
        s = self.state
        if s.get('version') != 1 or any(type(s.get(k)) is not int or s[k] < 0 for k in
                ('calls', 'input_tokens_accounted', 'output_tokens_accounted')):
            raise BudgetStop('invalid_ledger')
        # Recompute totals from journal entries to reject damaged accounting.
        entries = s.get('entries')
        if type(entries) is not list or len(entries) != s['calls']:
            raise BudgetStop('invalid_ledger')
        if any(type(e.get(k)) is not int or e[k] < 0 for e in entries for k in ('inputs', 'outputs')):
            raise BudgetStop('invalid_ledger')
        if (sum(e['inputs'] for e in entries) != s['input_tokens_accounted'] or
                sum(e['outputs'] for e in entries) != s['output_tokens_accounted'] or
                sum((self.config.cost(e['inputs'], e['outputs']) for e in entries), Decimal(0)) != Decimal(s['cost_accounted_usd'])):
            raise BudgetStop('invalid_ledger')
        unresolved = [e['request_id'] for e in entries if e['status'] != 'settled']
        if unresolved or s.get('pending'):
            # A crashed/ambiguous attempt could already have been billed. Do not resend it.
            raise BudgetStop('unresolved_charge_requires_reconciliation')

    def save(self):
        try:
            persist(self.path, self.state)
        except Exception:
            self.state['halted'] = 'ledger_storage_failure'
            raise BudgetStop('ledger_storage_failure') from None

    @synchronized
    def reserve(self, request_id):
        s, c = self.state, self.config
        if s['halted'] or s['pending']:
            raise BudgetStop(s['halted'] or 'request_in_flight')
        if s['calls'] + 1 > c.max_calls:
            raise BudgetStop('call_budget')
        if s['input_tokens_accounted'] + c.context_window > c.max_input_tokens:
            raise BudgetStop('input_token_budget')
        if s['output_tokens_accounted'] + c.output_tokens_per_call > c.max_output_tokens:
            raise BudgetStop('output_token_budget')
        if Decimal(s['cost_accounted_usd']) + c.reservation > Decimal(c.budget_usd):
            raise BudgetStop('dollar_budget')
        if any(e['request_id'] == request_id for e in s['entries']):
            raise BudgetStop('duplicate_request_id')
        s['calls'] += 1
        s['input_tokens_accounted'] += c.context_window
        s['output_tokens_accounted'] += c.output_tokens_per_call
        s['cost_accounted_usd'] = str(Decimal(s['cost_accounted_usd']) + c.reservation)
        s['pending'] = request_id
        s['entries'].append({'request_id': request_id, 'status': 'reserved',
                             'inputs': c.context_window, 'outputs': c.output_tokens_per_call})
        self.save()  # MUST complete before the transport can be called.

    @synchronized
    def uncertain(self, code):
        self.state['halted'] = code
        if self.state['pending']:
            self.state['entries'][-1]['status'] = 'uncertain'
        self.save()  # keep the entire reservation; no automatic refund/retry

    @synchronized
    def settle(self, request_id, usage):
        c, s = self.config, self.state
        keys = ('prompt_tokens', 'completion_tokens', 'total_tokens')
        if (type(usage) is not dict or any(type(usage.get(k)) is not int or usage[k] < 0 for k in keys)
                or usage['total_tokens'] != usage['prompt_tokens'] + usage['completion_tokens']):
            self.uncertain('missing_or_invalid_usage')
            raise BudgetStop('missing_or_invalid_usage')
        if s['pending'] != request_id:
            raise BudgetStop('reservation_mismatch')
        inputs, outputs = usage['prompt_tokens'], usage['completion_tokens']
        if inputs > c.context_window or outputs > c.output_tokens_per_call:
            self.uncertain('provider_exceeded_declared_limits')
            # No subsequent requests. Preserve observed counts for reconciliation.
            s['entries'][-1]['reported_usage'] = usage
            self.save()
            raise BudgetStop('provider_exceeded_declared_limits')
        s['input_tokens_accounted'] += inputs - c.context_window
        s['output_tokens_accounted'] += outputs - c.output_tokens_per_call
        s['cost_accounted_usd'] = str(Decimal(s['cost_accounted_usd']) - c.reservation + c.cost(inputs, outputs))
        s['entries'][-1].update(status='settled', inputs=inputs, outputs=outputs)
        s['pending'] = None
        self.save()

    @synchronized
    def halt(self, code):
        self.state['halted'] = code
        self.save()

    def close(self):
        if not self.lock.closed:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
