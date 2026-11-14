"""Real OS/client boundary checks. The relay is fake; no external network is allowed."""
import http.client
import json
from pathlib import Path
import socket
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from baseline.opencode_free.bridge import BASE,MODELS,Client,Ledger,Relay,config_for,write
from baseline.paid.run import PaidHistory


def main():
    out=ROOT/'artifacts/opencode-free-smoke/boundaries';out.mkdir(exist_ok=False)
    # A saved evaluator-only offline fixture supplies the observed frame at a real wipe.
    fixture=ROOT/'artifacts/paid-adapter-offline/proof'
    reports=[json.loads(p.read_text()) for p in fixture.glob('*/report.json')]
    wipe=next(r['wipes'][0] for r in reports if r['wipes'])
    history=PaidHistory();history.add(wipe['fresh_frame']);messages=history.messages()
    public=json.loads(messages[1]['content'])
    assert len(public['current_state']['notebook'])==8
    assert len(public['history_since_last_wipe']['events'])==1
    ledger=Ledger(out/'ledger.json')
    try:
        callout=out/'post-wipe';callout.mkdir()
        client=Client(MODELS[0],ledger,callout,live=False);client.complete(messages)
        call=callout/'call-01';verified=json.loads((call/'verified.json').read_text())
        state=ROOT/verified['fresh_state'];profile=call/'sandbox.sb'
        allowed=state/'canary.txt';allowed.write_text('public-canary')
        denied=out/'private-canary.txt';denied.write_text('private-canary')
        def cmd(args):
            return subprocess.run(['/usr/bin/sandbox-exec','-f',str(profile)]+args,
                                  capture_output=True,text=True,env={'PATH':'/usr/bin:/bin'},cwd=state/'work')
        assert cmd(['/bin/cat',str(allowed)]).stdout=='public-canary'
        assert cmd(['/bin/cat',str(denied)]).returncode!=0
        assert cmd(['/bin/cat',str(ROOT/'borderland/env.py')]).returncode!=0
        assert cmd(['/usr/bin/touch',str(out/'forbidden-write')]).returncode!=0
        # A different state directory is inaccessible, including transcripts from before a wipe.
        previous=next((BASE/'calls').glob('*/config'))
        assert previous.parent != state
        prior=previous.parent/'prior-private-canary';prior.write_text('pre-wipe transcript')
        assert cmd(['/bin/cat',str(prior)]).returncode!=0
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0));listener.listen()
            assert cmd(['/usr/bin/nc','-z','-w','1','127.0.0.1',str(listener.getsockname()[1])]).returncode!=0
        # Two identical transport requests produce exactly one fake upstream attempt.
        target=out/'duplicate';target.mkdir()
        relay=Relay(MODELS[1],messages,ledger,target,live=False);relay.start()
        payload={'model':MODELS[1],'stream':True,'stream_options':{'include_usage':True},
                 **config_for(MODELS[1],messages,1234)['providers']['opencode']['body']}
        statuses=[]
        try:
            for _ in range(2):
                conn=http.client.HTTPConnection('127.0.0.1',relay.server.server_port)
                conn.request('POST','/v1/chat/completions',json.dumps(payload),{'Authorization':'Bearer public','Content-Type':'application/json'})
                response=conn.getresponse();statuses.append(response.status);response.read();conn.close()
        finally:relay.close()
        assert statuses==[200,400]
        assert len(ledger.state['attempts'])==2  # one post-wipe client + one admitted duplicate-test request
        result={'all_checks_passed':True,'external_model_calls':0,'actual_client_post_wipe':True,
                'eight_line_notebook_only':True,'exact_post_wipe_request':True,
                'source_read_denied':True,'other_call_state_read_denied':True,'outside_write_denied':True,
                'other_local_port_denied':True,'duplicate_upstream_attempts':1,
                'note':'Post-wipe frame is an offline scripted fixture, never a live model performance result.'}
        write(out/'report.json',result);print(json.dumps(result,indent=2))
    finally:ledger.close()


if __name__=='__main__':main()
