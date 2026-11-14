"""Native Codex subscription requests through a one-attempt public-prompt relay."""
import base64
import copy
import fcntl
import hashlib
import http.client
import json
import os
import secrets
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from types import SimpleNamespace
from baseline.paid.config import local_path
from baseline.paid.client import ProviderStop,strict_json
from baseline.paid.budget import BudgetStop
from .native import BASE,AUTH_STATE,MODEL,CALLS,make_state,environment,command

EFFORT=os.environ.get('LEXI_TERRA_EFFORT','low')
if EFFORT not in ('low','medium','high'):raise ValueError('LEXI_TERRA_EFFORT must be low, medium or high')
CAP={'low':1024,'medium':6144,'high':12288}[EFFORT]
HTTP_TIMEOUT={'low':60,'medium':170,'high':280}[EFFORT]
NATIVE_TIMEOUT={'low':85,'medium':200,'high':310}[EFFORT]
UPSTREAM_HOST='chatgpt.com'
UPSTREAM_PATH='/backend-api/codex/responses'

def upstream_connection():
    """HTTPS connection to the fixed upstream host, through the sandbox's egress proxy when one is set."""
    import urllib.parse
    proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not proxy:return http.client.HTTPSConnection(UPSTREAM_HOST,timeout=HTTP_TIMEOUT)
    u=urllib.parse.urlsplit(proxy);headers={}
    if u.username:
        creds=urllib.parse.unquote(u.username)+':'+urllib.parse.unquote(u.password or '')
        headers['Proxy-Authorization']='Basic '+base64.b64encode(creds.encode()).decode()
    connection=http.client.HTTPSConnection(u.hostname,u.port or 3128,timeout=HTTP_TIMEOUT)
    connection.set_tunnel(UPSTREAM_HOST,443,headers=headers)
    return connection

def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

class Ledger:
    def __init__(self,path,*,live=False,max_calls=5):
        if type(max_calls) is not int or not 1 <= max_calls <= 100:
            raise ValueError('max_calls_must_be_integer_1_to_100')
        self.path=local_path(path);self.lock=self.path.with_suffix('.lock').open('a+')
        fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB);self.mutex=threading.Lock()
        self.state={'model':MODEL,'mode':'live' if live else 'offline','limit':max_calls,'attempts':[],'halt':None}
        try:
            if self.path.exists():
                self.state=json.loads(self.path.read_text())
                if (self.state['model']!=MODEL or self.state['mode']!=('live' if live else 'offline')
                    or self.state['limit']!=max_calls):raise ValueError('ledger_contract_mismatch')
                if any(r['status']=='pending' for r in self.state['attempts']):self.state['halt']='unresolved_attempt'
            self.save()
        except Exception:
            self.lock.close();raise
    def save(self):
        temp=self.path.with_suffix('.tmp')
        with temp.open('w') as f:json.dump(self.state,f);f.flush();os.fsync(f.fileno())
        os.replace(temp,self.path)
    def check(self):
        if self.state['halt']:raise BudgetStop(self.state['halt'])
        if len(self.state['attempts'])>=self.state['limit']:
            raise BudgetStop('five_call_limit' if self.state['limit']==5 else 'model_call_limit')
    def reserve(self,payload):
        with self.mutex:
            self.check();n=len(self.state['attempts'])+1
            self.state['attempts'].append({'number':n,'status':'pending','request_sha256':hashlib.sha256(payload).hexdigest()});self.save();return n
    def finish(self,n,**kwargs):
        with self.mutex:self.state['attempts'][n-1].update(kwargs);self.save()
    def halt(self,reason):
        with self.mutex:self.state['halt']=reason;self.save()
    def close(self):self.lock.close()

def auth_state(*,live):
    if live:
        path=AUTH_STATE/'state/auth.json'
        if not path.exists():raise ProviderStop('native_chatgpt_login_required')
        obj=strict_json(path.read_text())
        if obj.get('auth_mode')!='chatgpt' or obj.get('OPENAI_API_KEY'):
            raise ProviderStop('subscription_auth_required_api_keys_forbidden')
        tokens=obj.get('tokens') or {}
        if not all(isinstance(tokens.get(k),str) and tokens[k] for k in ['access_token','id_token']):
            raise ProviderStop('missing_subscription_tokens')
        return obj
    def b64(value):return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip('=')
    token=b64({'alg':'none'})+'.'+b64({'sub':'offline','exp':int(time.time())+3600,
          'https://api.openai.com/auth':{'chatgpt_account_id':'offline','chatgpt_plan_type':'pro'}})+'.offline'
    return {'auth_mode':'chatgpt','OPENAI_API_KEY':None,'tokens':{'id_token':token,'access_token':token,
            'refresh_token':'offline','account_id':'offline'},'last_refresh':'2026-11-14T00:00:00Z'}

def public_payload(messages):
    if len(messages)!=2 or [m['role'] for m in messages]!=['system','user']:raise ValueError('unexpected_public_message_shape')
    value={'model':MODEL,'instructions':messages[0]['content'],
        'input':[{'role':'user','content':[{'type':'input_text','text':messages[1]['content']}]}],
        'tools':[],'tool_choice':'none','parallel_tool_calls':False,'store':False,'stream':True,
        'reasoning':{'effort':EFFORT},'max_output_tokens':CAP}
    if len(json.dumps(value).encode())>64_000:raise ValueError('public_input_byte_limit')
    return value

def normalize(raw,messages):
    if raw.get('model')!=MODEL:raise ValueError('model_substitution_blocked')
    if raw.get('previous_response_id') or raw.get('conversation'):raise ValueError('provider_history_blocked')
    items=raw.get('input',[])
    users=[x for x in items if x.get('role')=='user']
    expected=[{'type':'input_text','text':messages[1]['content']}]
    if not users or users[-1].get('content')!=expected:raise ValueError('public_user_prompt_changed')
    if not any(x.get('role')=='developer' and x.get('content')==[{'type':'input_text','text':messages[0]['content']}] for x in items):
        raise ValueError('public_system_prompt_changed')
    # Exclude native coding tools, skills and environment boilerplate. Never add game facts.
    return public_payload(messages)

def fake_sse():
    text=json.dumps({'reason':'offline guard fixture','tool':'inspect','args':{'object_id':'rules'}})
    msg={'type':'message','id':'msg_offline','role':'assistant','status':'completed',
         'content':[{'type':'output_text','text':text,'annotations':[]}]}
    events=[{'type':'response.created','response':{'id':'resp_offline','status':'in_progress','output':[]}},
      {'type':'response.output_item.added','output_index':0,'item':{**msg,'status':'in_progress','content':[]}},
      {'type':'response.output_text.delta','item_id':'msg_offline','output_index':0,'content_index':0,'delta':text},
      {'type':'response.output_item.done','output_index':0,'item':msg},
      {'type':'response.completed','response':{'id':'resp_offline','model':MODEL,'status':'completed','max_output_tokens':CAP,
       'output':[msg],'usage':{'input_tokens':100,'output_tokens':20,'total_tokens':120}}}]
    return ''.join('event: '+e['type']+'\ndata: '+json.dumps(e)+'\n\n' for e in events).encode()

def parse_sse(data):
    completed=None
    for line in data.decode().splitlines():
        if not line.startswith('data: '):continue
        obj=strict_json(line[6:])
        if obj.get('type') in ['response.failed','response.incomplete','error']:raise ValueError('incomplete_or_failed_response')
        if obj.get('type')=='response.completed':completed=obj['response']
    if not completed or completed.get('status')!='completed':raise ValueError('no_complete_response')
    if completed.get('model') not in (None,MODEL):raise ValueError('returned_model_mismatch')
    if completed.get('max_output_tokens') not in (None,CAP):raise ValueError('returned_output_cap_mismatch')
    usage=completed.get('usage')
    if not isinstance(usage,dict) or not isinstance(usage.get('output_tokens'),int):raise ValueError('missing_usage')
    if usage['output_tokens']>CAP:raise ValueError('output_cap_exceeded')
    messages=[]
    for item in completed.get('output',[]):
        if item.get('type')=='reasoning':continue
        if item.get('type')!='message' or item.get('role')!='assistant':raise ValueError('non_message_output')
        for part in item.get('content',[]):
            if part.get('type')!='output_text':raise ValueError('non_text_output')
            messages.append(part['text'])
    return ''.join(messages),usage

def settings(state,port):
    return {'forced_login_method':'chatgpt','cli_auth_credentials_store':'file','model_provider':'subscription_bridge',
        'model_providers.subscription_bridge.name':'Native Codex subscription bridge',
        'model_providers.subscription_bridge.base_url':f'http://127.0.0.1:{port}/v1',
        'model_providers.subscription_bridge.wire_api':'responses','model_providers.subscription_bridge.requires_openai_auth':True,
        'model_providers.subscription_bridge.request_max_retries':0,'model_providers.subscription_bridge.stream_max_retries':0,
        'model_providers.subscription_bridge.supports_websockets':False,
        'model_instructions_file':str(state/'system.txt'),'model_reasoning_effort':EFFORT,
        'features.shell_tool':False,'features.shell_snapshot':False,'features.view_image':False,
        'features.apps':False,'features.codex_hooks':False,'agents.enabled':False,'web_search':'disabled',
        'project_doc_max_bytes':0,'check_for_update_on_startup':False}

class Relay:
    def __init__(self,messages,auth,ledger,folder,*,live=False):
        self.used=False;self.error=None;self.text=None;self.lock=threading.Lock()
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):self.send_error(404,'remote metadata disabled; use bundled catalog')
            def do_POST(self):
                number=None
                try:
                    with owner.lock:
                        if owner.used:raise ValueError('retry_or_extra_call_blocked')
                        owner.used=True
                    if self.path!='/v1/responses':raise ValueError('endpoint_blocked')
                    size=int(self.headers.get('Content-Length',0))
                    if not 0<size<=256_000:raise ValueError('native_request_byte_limit')
                    incoming=self.rfile.read(size);raw=strict_json(incoming.decode())
                    payload=normalize(raw,messages)
                    if self.headers.get('Authorization')!='Bearer '+auth['tokens']['access_token']:
                        raise ValueError('subscription_credential_mismatch')
                    (folder/'native-request.json').write_bytes(incoming)
                    outgoing=json.dumps(payload,separators=(',',':')).encode()
                    (folder/'request.json').write_bytes(outgoing)
                    number=ledger.reserve(outgoing)
                    if live:
                        headers={k:v for k,v in self.headers.items() if k.lower() not in {
                            'host','connection','content-length','accept-encoding','x-openai-internal-codex-responses-lite'}}
                        connection=upstream_connection()
                        try:
                            connection.request('POST',UPSTREAM_PATH,body=outgoing,headers=headers)
                            response=connection.getresponse();status=response.status;data=response.read(2_000_001)
                            write(folder/'upstream.json',{'status':status,'headers':{k:v for k,v in response.getheaders()
                                  if k.lower() in ['content-type','retry-after','x-request-id']}})
                        finally:connection.close()
                    else:status,data=200,fake_sse()
                    if len(data)>2_000_000:raise ValueError('response_byte_limit')
                    (folder/'response.sse').write_bytes(data)
                    if status!=200:raise ValueError('subscription_http_'+str(status))
                    owner.text,usage=parse_sse(data)
                    ledger.finish(number,status='complete',usage=usage)
                    self.send_response(200);self.send_header('Content-Type','text/event-stream')
                    self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                except Exception as e:
                    owner.error=owner.error or str(e)
                    if number:ledger.finish(number,status='failed',error=owner.error)
                    ledger.halt(owner.error)
                    with (folder/'blocked.jsonl').open('a') as f:f.write(json.dumps({'reason':str(e)})+'\n')
                    try:self.send_error(400,'bridge stopped')
                    except OSError:pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
    def start(self):self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()

class Client:
    def __init__(self,ledger,folder,*,live=False):
        self.ledger,self.folder,self.live=ledger,local_path(folder),live
        self.config=SimpleNamespace(no_progress_limit=3);self.calls=0
    def complete(self,messages):
        self.ledger.check();self.calls+=1
        folder=self.folder/f'call-{self.calls:02d}';folder.mkdir(exist_ok=False)
        write(folder/'public-messages.json',messages)
        state=make_state(CALLS/secrets.token_hex(12))
        auth=auth_state(live=self.live)
        authpath=state/'state/auth.json';write(authpath,auth);authpath.chmod(0o600)
        (state/'system.txt').write_text(messages[0]['content'])
        relay=Relay(messages,auth,self.ledger,folder,live=self.live);relay.start()
        opts=settings(state,relay.server.server_port);write(folder/'config.json',opts)
        args=command(state,relay_port=relay.server.server_port)+['exec','--ignore-user-config','--ignore-rules',
            '--ephemeral','--skip-git-repo-check','--sandbox','read-only','--model',MODEL,'--json','-']
        for key,value in opts.items():args+=['-c',key+'='+json.dumps(value)]
        try:
            proc=subprocess.run(args,input=messages[1]['content'],env=environment(state),cwd=state/'work',
                                capture_output=True,text=True,timeout=NATIVE_TIMEOUT)
            (folder/'cli.jsonl').write_text(proc.stdout);(folder/'cli.stderr').write_text(proc.stderr)
            if relay.error:raise ProviderStop(relay.error)
            if proc.returncode or relay.text is None:raise ProviderStop('native_client_failed')
            events=[strict_json(x) for x in proc.stdout.splitlines() if x.strip()]
            texts=[e['item']['text'] for e in events if e['type']=='item.completed' and e.get('item',{}).get('type')=='agent_message']
            if ''.join(texts)!=relay.text:raise ProviderStop('native_response_mismatch')
            if len([e for e in events if e['type']=='turn.completed'])!=1:raise ProviderStop('extra_native_turn')
            write(folder/'verified.json',{'native_codex':True,'model':MODEL,'live':self.live,
                 'state':state.name,'thread_ids':[e['thread_id'] for e in events if e['type']=='thread.started'],
                 'exact_public_payload':True,'tools_removed':True,'api_key_present':False})
            return relay.text
        except (subprocess.TimeoutExpired,OSError,ProviderStop) as e:
            self.ledger.halt(str(e));raise ProviderStop(str(e)) from e
        finally:
            relay.close()
            # No credentials are retained in per-decision state. The login cache stays private.
            if authpath.exists():authpath.unlink()
