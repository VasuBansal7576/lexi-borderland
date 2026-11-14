import copy
import fcntl
import hashlib
import http.client
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

from baseline.paid.client import ProviderStop, strict_json
from baseline.paid.budget import BudgetStop
from baseline.paid.config import ROOT, local_path

MODELS = ('inkling-2-small-free', 'longcat-2.5-free', 'nemotron-3.5-super-vl-free',
          'glm-5.3-flash-free', 'minimax-m3.1-flash-free')
BASE = ROOT/'runtime/opencode-bridge'
INSTALL = BASE/'client/install'
BINARY = INSTALL/'package/bin/opencode'
ENDPOINT = '/inference/openai/v1/chat/completions'
OUTPUT_CAP = 1024
INPUT_BYTES = 64_000  # hard request-byte ceiling, deliberately not a token estimate
RESPONSE_BYTES = 2_000_000


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


class Ledger:
    """Count actual upstream attempts BEFORE sending. Interrupted attempts remain spent."""
    def __init__(self, path, *, live=False):
        self.path = local_path(path)
        self.lock = self.path.with_suffix('.lock').open('a+')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.mutex = threading.Lock()
        self.state = {'mode': 'live' if live else 'offline', 'attempts': [], 'halts': {},
                      'limit_per_model': 5, 'limit_total': 25, 'output_cap': OUTPUT_CAP}
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
            if self.state['mode'] != ('live' if live else 'offline'):
                raise ValueError('ledger mode mismatch')
            for row in self.state['attempts']:
                if row['status'] == 'pending':
                    self.state['halts'][row['model']] = 'unresolved_prior_attempt'
        self.save()

    def save(self):
        temp = self.path.with_suffix('.tmp')
        with temp.open('w') as f:
            json.dump(self.state, f, allow_nan=False); f.flush(); os.fsync(f.fileno())
        os.replace(temp, self.path)

    def check(self, model):
        if model not in MODELS: raise BudgetStop('model_not_free_allowlisted')
        if model in self.state['halts']: raise BudgetStop(self.state['halts'][model])
        if len(self.state['attempts']) >= 25: raise BudgetStop('total_call_limit')
        if sum(x['model'] == model for x in self.state['attempts']) >= 5:
            raise BudgetStop('five_call_limit')

    def reserve(self, model, digest):
        with self.mutex:
            self.check(model)
            row = {'number': len(self.state['attempts'])+1, 'model': model,
                   'request_sha256': digest, 'status': 'pending'}
            self.state['attempts'].append(row); self.save()
            return row['number']

    def finish(self, number, **details):
        with self.mutex:
            self.state['attempts'][number-1].update(details); self.save()

    def halt_model(self, model, reason):
        with self.mutex:
            self.state['halts'][model] = reason; self.save()

    def close(self):
        self.lock.close()


class ModelLedger:
    def __init__(self, ledger, model): self.parent, self.model = ledger, model
    @property
    def state(self): return self.parent.state
    def halt(self, reason): self.parent.halt_model(self.model, reason)


def validate_payload(payload, model, messages):
    if model not in MODELS or payload.get('model') != model:
        raise ValueError('model_mismatch_or_paid')
    if payload.get('messages') != messages: raise ValueError('public_messages_changed')
    if payload.get('tools') != [] or payload.get('tool_choice') != 'none':
        raise ValueError('external_tools_exposed')
    if payload.get('stream') is not True or payload.get('stream_options') != {'include_usage': True}:
        raise ValueError('usage_stream_required')
    if payload.get('max_completion_tokens') != OUTPUT_CAP:
        raise ValueError('output_cap_missing')
    allowed = {'model','messages','tools','tool_choice','stream','stream_options','max_completion_tokens','max_tokens'}
    if set(payload)-allowed: raise ValueError('unexpected_request_fields')
    if 'max_tokens' in payload and payload['max_tokens'] != OUTPUT_CAP:
        raise ValueError('output_cap_conflict')
    if len(json.dumps(payload).encode()) > INPUT_BYTES: raise ValueError('input_byte_limit')


def sandbox_profile(state, control_port, relay_port):
    """Deny personal/project content except this single call's state and official executable."""
    state = local_path(state)
    return f'''(version 1)
(allow default)
(deny network-outbound (require-all
 (require-not (remote ip "localhost:{control_port}"))
 (require-not (remote ip "localhost:{relay_port}"))))
(deny network-inbound (require-not (local ip "localhost:{control_port}")))
(deny file-read-data (require-all
 (require-not (subpath "{state}")) (require-not (subpath "{INSTALL}"))
 (require-any (subpath "/Users") (subpath "/Volumes")
 (subpath "/private/var/folders") (subpath "/var/folders")
 (subpath "/private/tmp") (subpath "/tmp")
 (subpath "/Library/Application Support") (subpath "/Library/Managed Preferences"))))
(deny file-write* (require-not (subpath "{state}")))
'''


def config_for(model, messages, port):
    deny = [{'action':'*','resource':'*','effect':'deny'}]
    actions = ['provider.use','tool.use','integration.connect','integration.use',
               'mcp.use','skill.use','plugin.use','websearch.use']
    return {'model': 'opencode/'+model, 'default_agent':'player', 'update':'disable',
        'share':'disabled','snapshots':False,'warming':False,'formatter':False,
        'lsp':False,'websearch':False,'instructions':[],'skills':[],'plugins':[],
        'watcher':{'ignore':['**/*']},'compaction':{'auto':False}, 'permissions':deny,
        'policies':[{'action':a,'resource':'*','effect':'deny'} for a in actions] +
                   [{'action':a,'resource':'opencode','effect':'allow'} for a in ['provider.use','integration.use']],
        'agents':{**{a:{'disabled':True} for a in ['title','summary','compaction','build','plan','explore','general']},
                  'player':{'mode':'primary','steps':2,'system':messages[0]['content'],'permissions':deny}},
        'providers':{'opencode':{
            'settings':{'baseURL':f'http://127.0.0.1:{port}/v1','encoding':'none','timeout':65000,
                        'cache':{'warming':False}},
            'models':{model:{'limit':{'output':OUTPUT_CAP}}},
            'body':{'messages':messages,'tools':[],'tool_choice':'none','max_completion_tokens':OUTPUT_CAP}}}}


def isolated_env(state, config):
    result = {'PATH':'/usr/bin:/bin', 'TMPDIR':str(state/'tmp'),
              'OPENCODE_PASSWORD':secrets.token_hex(24),
              'OPENCODE_DISABLE_PROJECT_CONFIG':'1','OPENCODE_CONFIG_CONTENT':json.dumps(config),
              'OPENCODE_CLI_CONFIG_CONTENT':'{}'}
    for key, folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),
                        ('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
        result[key] = str(state/folder)
    return result


def fake_response(model):
    action = json.dumps({'reason':'offline transport fixture','tool':'inspect','args':{'object_id':'rules'}})
    chunks = [ {'id':'offline','object':'chat.completion.chunk','model':model,
                'choices':[{'index':0,'delta':{'role':'assistant','content':action},'finish_reason':None}]},
               {'id':'offline','object':'chat.completion.chunk','model':model,
                'choices':[{'index':0,'delta':{},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120,
                         'cost':0,'opencode':{'billing_source':'free'}}}]
    return (''.join('data: '+json.dumps(c)+'\n\n' for c in chunks)+'data: [DONE]\n\n').encode()


def parse_stream(raw, model):
    text, usage, finish = [], None, None
    for line in raw.decode().splitlines():
        if not line.startswith('data: ') or line == 'data: [DONE]': continue
        obj = strict_json(line[6:])
        # Provider may identify the underlying model instead of its free routing alias.
        for choice in obj.get('choices', []):
            if choice.get('index', 0) != 0: raise ValueError('multiple_completions')
            delta = choice.get('delta', {})
            if delta.get('tool_calls') or delta.get('function_call'): raise ValueError('tool_call_response')
            if delta.get('content'): text.append(delta['content'])
            if choice.get('finish_reason'): finish = choice['finish_reason']
        if obj.get('usage'): usage = obj['usage']
    if finish != 'stop': raise ValueError('incomplete_output_'+str(finish))
    if not usage or usage.get('cost') != 0 or usage.get('opencode',{}).get('billing_source') != 'free':
        raise ValueError('free_usage_not_confirmed')
    return ''.join(text), usage


class Relay:
    def __init__(self, model, messages, ledger, folder, *, live=False):
        self.model, self.messages, self.ledger, self.folder = model, copy.deepcopy(messages), ledger, folder
        self.live, self.used, self.error, self.raw, self.text = live, False, None, None, None
        self.lock = threading.Lock()
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self): self.send_error(403, 'metadata access disabled')
            def do_POST(self):
                try:
                    with owner.lock:
                        if owner.used: raise ValueError('retry_or_background_call_blocked')
                        owner.used = True  # each process gets one attempt, even when rejected
                    if self.path != '/v1/chat/completions': raise ValueError('endpoint_blocked')
                    size = int(self.headers.get('Content-Length', 0))
                    if not 0 < size <= INPUT_BYTES: raise ValueError('input_byte_limit')
                    raw = self.rfile.read(size)
                    payload = strict_json(raw.decode())
                    validate_payload(payload, model, messages)
                    if self.headers.get('Authorization') != 'Bearer public':
                        raise ValueError('signed_in_credentials_blocked')
                    (folder/'request.json').write_bytes(raw)
                    write(folder/'client-headers.json', {k:v for k,v in self.headers.items()
                          if k.lower() not in {'authorization','cookie'}})
                    number = ledger.reserve(model, hashlib.sha256(raw).hexdigest())
                    try:
                        if live:
                            # Forward the real official client's headers; never synthesize client identity.
                            headers = {k:v for k,v in self.headers.items() if k.lower() not in
                                       {'host','connection','content-length','accept-encoding'}}
                            conn = http.client.HTTPSConnection('opencode.ai', timeout=60)
                            try:
                                conn.request('POST', ENDPOINT, body=raw, headers=headers)
                                response = conn.getresponse()
                                data = response.read(RESPONSE_BYTES+1)
                                status = response.status
                                write(folder/'upstream.json', {'status':status,
                                      'headers':{k:v for k,v in response.getheaders() if k.lower() in
                                                 {'content-type','retry-after','x-request-id'}}})
                            finally: conn.close()
                        else: data, status = fake_response(model), 200
                        if len(data) > RESPONSE_BYTES: raise ValueError('response_byte_limit')
                        (folder/'response.sse').write_bytes(data)
                        if status != 200: raise ValueError('upstream_http_'+str(status))
                        owner.raw = data
                        owner.text, usage = parse_stream(data, model)
                        ledger.finish(number, status='complete', usage=usage)
                        self.send_response(200);self.send_header('Content-Type','text/event-stream')
                        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                    except Exception as e:
                        ledger.finish(number, status='failed', error=str(e)); raise
                except Exception as e:
                    owner.error = owner.error or str(e)
                    ledger.halt_model(model, owner.error)
                    with (folder/'blocked.jsonl').open('a') as f:
                        f.write(json.dumps({'reason':str(e)})+'\n')
                    try: self.send_error(400, 'bridge stopped: '+owner.error)
                    except OSError: pass
        self.server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self): self.thread.start()
    def close(self): self.server.shutdown(); self.server.server_close(); self.thread.join()


class Client:
    def __init__(self, model, ledger, folder, *, live=False):
        if model not in MODELS: raise ValueError('free model required')
        self.model, self.parent, self.folder, self.live = model, ledger, local_path(folder), live
        self.ledger, self.config = ModelLedger(ledger, model), SimpleNamespace(no_progress_limit=3)
        self.calls = 0

    def complete(self, messages):
        self.parent.check(self.model)
        self.calls += 1
        folder = self.folder/f'call-{self.calls:02d}'; folder.mkdir(exist_ok=False)
        write(folder/'public-messages.json', messages)
        state = BASE/'calls'/secrets.token_hex(12)
        for name in ['work','tmp/opencode','config','data','cache','state']:
            (state/name).mkdir(parents=True, exist_ok=True)
        relay = Relay(self.model, messages, self.parent, folder, live=self.live)
        with socket.socket() as s:
            s.bind(('127.0.0.1',0)); control_port = s.getsockname()[1]
        profile = sandbox_profile(state, control_port, relay.server.server_port)
        (folder/'sandbox.sb').write_text(profile)
        cfg = config_for(self.model, messages, relay.server.server_port)
        write(folder/'config.json', cfg)
        env = isolated_env(state, cfg)
        prefix = ['/usr/bin/sandbox-exec','-f',str(folder/'sandbox.sb'),str(BINARY)]
        control = None; relay.start()
        log = (folder/'control.log').open('w')
        try:
            control = subprocess.Popen(prefix+['serve','--hostname','127.0.0.1','--port',str(control_port)],
                env=env, cwd=state/'work', stdout=log, stderr=log, start_new_session=True)
            deadline = time.monotonic()+15
            while True:
                if control.poll() is not None: raise ProviderStop('private_control_server_failed')
                try:
                    with socket.create_connection(('127.0.0.1',control_port),timeout=.2): break
                except OSError:
                    if time.monotonic()>deadline: raise ProviderStop('private_control_server_timeout')
                    time.sleep(.05)
            args = prefix+['run','--server',f'http://127.0.0.1:{control_port}',
                '--model','opencode/'+self.model,'--agent','player','--format','json',
                '--title','Borderland isolated action', 'Choose one action from the supplied public game state.']
            proc = subprocess.run(args, cwd=state/'work', env=env, capture_output=True, text=True, timeout=80)
            (folder/'cli.jsonl').write_text(proc.stdout)
            (folder/'cli.stderr').write_text(proc.stderr)
            if relay.error: raise ProviderStop(relay.error)
            if proc.returncode or relay.text is None: raise ProviderStop('client_failed_before_valid_response')
            events = [strict_json(line) for line in proc.stdout.splitlines() if line.strip()]
            text = ''.join(e['part']['text'] for e in events if e['type']=='text')
            finishes = [e for e in events if e['type']=='step_finish']
            if text != relay.text or len(finishes)!=1 or any(e['type']=='error' for e in events):
                raise ProviderStop('cli_response_mismatch')
            write(folder/'verified.json', {'exact_public_payload':True,'no_coding_tools':True,
                'fresh_state':str(state.relative_to(ROOT)), 'session_ids':sorted(set(e.get('sessionID') for e in events)),
                'upstream_attempts':1,'live':self.live,'output_cap':OUTPUT_CAP})
            return text
        except (subprocess.TimeoutExpired, OSError) as e:
            self.ledger.halt(type(e).__name__); raise ProviderStop(type(e).__name__) from e
        except ProviderStop as e:
            self.ledger.halt(str(e)); raise
        finally:
            if control and control.poll() is None:
                os.killpg(control.pid, signal.SIGTERM)
                try: control.wait(timeout=5)
                except subprocess.TimeoutExpired: os.killpg(control.pid, signal.SIGKILL);control.wait()
            log.close();relay.close()
