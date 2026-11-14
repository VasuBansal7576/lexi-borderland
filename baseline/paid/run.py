"""One unassisted episode. No reference solver, reference prefix or gold notebook."""
import argparse
import copy
import hashlib
import json
from decimal import Decimal
from .config import Config, ROOT, local_path
from .budget import Ledger, BudgetStop
from .client import Client, HTTPTransport, ProviderStop, strict_json
from .guard import LoopGuard
from ..interface_v3 import PublicHistory, response_schema, validate, unpack, canonical
from borderland.env import BorderlandEnv


class PaidHistory(PublicHistory):
    def messages(self):
        messages = super().messages()
        messages[0]['content'] = messages[0]['content'].replace(
            'Exiting room 3 destroys the transcript and model cache.',
            'Exiting room 3 clears the supplied transcript. Each API request is stateless; no previous response or conversation ID is reused.')
        return messages


def explain_invalid(raw, observation):
    """Name the violated rule for the tool the model chose, without revealing anything latent."""
    from ..interface_v2 import PARAMETERS, obj
    try:
        output = strict_json(raw)
    except Exception:
        return 'output is not one strict JSON object'
    if not isinstance(output, dict) or set(output) != {'reason', 'tool', 'args'}:
        return 'output must be an object with exactly reason, tool, args'
    if output['tool'] not in observation['tools']:
        return f"tool {output['tool']!r} is not available in this room"
    branch = obj({'reason': {'type': 'string', 'maxLength': 600}, 'tool': {'const': output['tool']},
                  'args': copy.deepcopy(PARAMETERS[output['tool']])})
    try:
        validate(output, branch)
    except AssertionError as error:
        return f"arguments for {output['tool']} violate its schema: {error}"
    return None


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


class EventLog:
    def __init__(self, path):
        self.file = path.open('x')

    def __call__(self, value):
        self.file.write(json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n')
        self.file.flush()

    def close(self):
        self.file.close()


def run_episode(env, client, folder, *, mode, resume_actions=None, pause_after_seconds=None, invalid_action='halt'):
    # resume_actions: previously recorded rows (with the model's raw output) replayed WITHOUT model calls,
    # so an episode can continue across process restarts. pause_after_seconds: stop cleanly (no ledger halt)
    # before starting a new model call once this much wall time has passed; rerun with resume to continue.
    import time
    started = time.monotonic()
    pending = list(resume_actions or [])
    # invalid_action='halt' (original fail-fast) or 'error_frame': the model sees a failed result naming the
    # violated schema rule; the environment is not stepped; 3 consecutive invalid outputs end the episode.
    consecutive_invalid, invalid_count = 0, 0
    folder = local_path(folder)
    # Caller creates output once; each episode gets a fresh history and public projection.
    history, guard = PaidHistory(), LoopGuard(client.config.no_progress_limit)
    frame = {'ok': True, 'result': {}, 'observation': env.observe()}
    actions, wipes, stop = [], [], None
    write(folder/'manifest.json', env.world)  # evaluator artifact, NEVER sent to client
    while not (env.terminated or env.truncated):
        history.add(frame)
        original = copy.deepcopy(history.frames)
        for item in original:
            item['observation'].pop('tools')
        if unpack(history.pack()) != original:
            stop = 'history_codec_failure'
            client.ledger.halt(stop)
            break
        if pending:
            row = pending.pop(0)
            if canonical(row['public_frame']) != canonical(frame):
                raise AssertionError('resume replay diverged from recorded public frame')
            raw = row['raw']
        else:
            if pause_after_seconds is not None and time.monotonic() - started > pause_after_seconds:
                stop = 'chunk_paused'
                break
            try:
                raw = client.complete(history.messages())
            except (BudgetStop, ProviderStop) as error:
                stop = str(error)
                break
        try:
            output = strict_json(raw)
            validate(output, response_schema(frame['observation']))
            action = {'tool': output['tool'], 'args': output['args']}
        except Exception as error:
            if invalid_action != 'error_frame':
                # The paid policy is fail-fast: do not spend another call on repair.
                stop = 'invalid_model_action'
                client.ledger.halt(stop)
                break
            detail = explain_invalid(raw, frame['observation']) or str(error)
            consecutive_invalid += 1; invalid_count += 1
            history.act({'invalid_output': raw[:1500]})
            before = frame
            frame = {'ok': False, 'result': {'error': 'invalid_action', 'detail': detail}, 'observation': before['observation']}
            actions.append({'public_frame': before, 'raw': raw, 'action': None, 'invalid': detail, 'output': frame})
            write(folder/'actions.json', actions)
            if consecutive_invalid >= 3:
                stop = 'repeated_invalid_actions'
                break
            continue
        consecutive_invalid = 0
        history.act(output)
        before = frame
        result = env.step(action)
        actions.append({'public_frame': before, 'raw': raw, 'action': action, 'output': result.observation})
        write(folder/'actions.json', actions)
        if result.info['epoch_changed']:
            note = list(env.notebook)
            history, guard = PaidHistory(), LoopGuard(client.config.no_progress_limit)
            frame = {'ok': True, 'result': {}, 'observation': env.observe()}
            wipes.append({'after_action': len(actions)-1, 'notebook': note, 'fresh_frame': frame,
                          'boundary': 'stateless request; old history discarded; no provider cache-deletion claim'})
        else:
            frame = result.observation
            stalled = guard.observe(before, action, frame)
            if stalled and not (env.terminated or env.truncated):
                stop = 'evaluator_no_progress'
                client.ledger.halt(stop)
                break
    if stop == 'chunk_paused':
        report = {'mode': mode, 'stop': stop, 'actions': len(actions), 'last_room': env.room, 'wipes': wipes,
                  'success': False, 'exact_replay': None, 'resume': True}
        write(folder/'paused.json', report)
        return report
    replay = BorderlandEnv(world=env.world)
    for row in env.trace:
        replay.step(row['action'])
        if canonical(row) != canonical(replay.trace[-1]):
            raise AssertionError('environment replay mismatch')
    (folder/'trace.jsonl').write_text(''.join(canonical(row)+'\n' for row in env.trace))
    report = {'mode': mode, 'success': env.success, 'stop': stop or env.reason,
              'external_stop': stop is not None, 'environment_reason': env.reason,
              'environment_terminated': env.terminated, 'environment_truncated': env.truncated,
              'actions': len(actions), 'invalid_actions': invalid_count, 'invalid_action_policy': invalid_action,
              'last_room': env.room, 'wipes': wipes,
              'score': env.score, 'integrity': env.integrity, 'exact_replay': True,
              'ledger': copy.deepcopy(client.ledger.state),
              'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(list((ROOT/'borderland').glob('*.py')) + list((ROOT/'baseline/paid').glob('*.py')) +
                                               [ROOT/'baseline/interface_v2.py', ROOT/'baseline/interface_v3.py', ROOT/'baseline/public_rules.txt'])}}
    write(folder/'report.json', report)
    return report


class OfflineDemoTransport:
    """Deliberately stalled synthetic policy, not a model or a reference solution."""
    def send(self, payload, request_id):
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps(
            {'reason': 'offline synthetic repeat test', 'tool': 'inspect', 'args': {'object_id': 'rules'}})}}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 30, 'total_tokens': 130}}


def main():
    parser = argparse.ArgumentParser(description='Paid adapter; default is offline preflight, never network.')
    parser.add_argument('--config', required=True)
    parser.add_argument('--manifest', default='artifacts/certification-v1/family-0000/phase-0-sigma-0/manifest.json')
    parser.add_argument('--output')
    parser.add_argument('--ledger')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--live', action='store_true')
    mode.add_argument('--offline-demo', action='store_true')
    args = parser.parse_args()
    config = Config.read(args.config)
    env = BorderlandEnv(world=json.loads(local_path(args.manifest).read_text()))
    history = PaidHistory(); history.add({'ok': True, 'result': {}, 'observation': env.observe()})
    if not args.live and not args.offline_demo:
        print(json.dumps({'mode': 'offline_preflight', 'network_calls': 0,
                          'model': config.model, 'maximum_reserved_usd_per_request': str(config.reservation),
                          'budget_usd': config.budget_usd, 'call_limit': config.max_calls,
                          'first_request_affordable': (config.reservation <= Decimal(config.budget_usd)
                              and config.context_window <= config.max_input_tokens
                              and config.output_tokens_per_call <= config.max_output_tokens),
                          'public_messages_utf8_bytes': len(json.dumps(history.messages()).encode()),
                          'note': 'Bytes are NOT a token estimate. Live provider/pricing compatibility is not verified.'}, indent=2))
        return
    if not args.output or not args.ledger:
        parser.error('--output and --ledger are required for a run')
    folder = local_path(args.output); ledger_path = local_path(args.ledger)
    if folder.exists():
        parser.error('output must be a fresh directory')
    if ledger_path == folder or ledger_path.is_relative_to(folder):
        parser.error('keep the reusable ledger outside the per-run output folder')
    # No credential read or HTTP transport construction in either offline mode.
    transport = HTTPTransport(config, live=True) if args.live else OfflineDemoTransport()
    ledger = Ledger(config, ledger_path)
    log = None
    try:
        folder.mkdir(parents=True, exist_ok=False)
        log = EventLog(folder/'events.jsonl')
        report = run_episode(env, Client(config, ledger, transport, log), folder,
                             mode='live' if args.live else 'offline_fake')
        print(json.dumps({k: report[k] for k in ('mode', 'success', 'stop', 'actions', 'last_room')}, indent=2))
    finally:
        if log: log.close()
        ledger.close()


if __name__ == '__main__':
    main()
