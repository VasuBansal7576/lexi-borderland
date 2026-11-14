import http.client,json,socket,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from baseline.codex_subscription.bridge import BASE,Client,Ledger,Relay,auth_state,write
from baseline.paid.run import PaidHistory

def main():
    out=ROOT/'artifacts/codex-subscription-smoke/boundaries';out.mkdir(exist_ok=False)
    reports=[json.loads(p.read_text()) for p in (ROOT/'artifacts/paid-adapter-offline/proof').glob('*/report.json')]
    wipe=next(r['wipes'][0] for r in reports if r['wipes'])
    history=PaidHistory();history.add(wipe['fresh_frame']);messages=history.messages()
    public=json.loads(messages[1]['content']);assert len(public['current_state']['notebook'])==8
    assert len(public['history_since_last_wipe']['events'])==1
    ledger=Ledger(out/'ledger.json')
    try:
        target=out/'post-wipe';target.mkdir();Client(ledger,target).complete(messages)
        proof=json.loads((target/'call-01/verified.json').read_text());state=BASE/proof['state']
        assert not (state/'state/auth.json').exists()
        allowed=state/'canary';allowed.write_text('public')
        hidden=out/'canary';hidden.write_text('private')
        def run(args):return subprocess.run(['/usr/bin/sandbox-exec','-f',str(state/'sandbox.sb')]+args,
                         cwd=state/'work',env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
        assert run(['/bin/cat',str(allowed)]).stdout=='public'
        for path in [hidden,ROOT/'borderland/env.py',BASE/'native-auth/state/auth.json']:
            assert run(['/bin/cat',str(path)]).returncode!=0
        assert run(['/usr/bin/touch',str(out/'forbidden-write')]).returncode!=0
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));sock.listen()
            assert run(['/usr/bin/nc','-z','-w','1','127.0.0.1',str(sock.getsockname()[1])]).returncode!=0
        target=out/'duplicate';target.mkdir();auth=auth_state(live=False)
        relay=Relay(messages,auth,ledger,target);relay.start()
        request={'model':'gpt-6.1-terra','input':[{'role':'developer','content':[{'type':'input_text','text':messages[0]['content']}]},
                      {'role':'user','content':[{'type':'input_text','text':messages[1]['content']}]}]}
        statuses=[]
        try:
            for _ in range(2):
                conn=http.client.HTTPConnection('127.0.0.1',relay.server.server_port)
                conn.request('POST','/v1/responses',json.dumps(request),{'Authorization':'Bearer '+auth['tokens']['access_token'],'Content-Type':'application/json'})
                response=conn.getresponse();statuses.append(response.status);response.read();conn.close()
        finally:relay.close()
        assert statuses==[200,400] and len(ledger.state['attempts'])==2
        result={'all_checks_passed':True,'external_model_calls':0,'native_codex_only':True,
                'exact_post_wipe_payload':True,'eight_line_notebook':True,'hidden_source_read_denied':True,
                'master_credential_read_denied':True,'outside_write_denied':True,'other_local_port_denied':True,
                'per_call_credentials_removed':True,'duplicate_forwarded_attempts':1,
                'note':'Post-wipe public frame is an offline scripted fixture, not a live model result.'}
        write(out/'report.json',result);print(json.dumps(result,indent=2))
    finally:ledger.close()

if __name__=='__main__':main()
