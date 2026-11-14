"""Reconstruct the subscription model's evidence from raw actions and the unchanged environment."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from baseline.codex_subscription.bridge import public_payload,normalize,parse_sse,write
from baseline.paid.run import PaidHistory
from baseline.paid.client import strict_json
from baseline.interface_v3 import validate,response_schema,canonical
from borderland.env import BorderlandEnv

def audit(folder):
    report=json.loads((folder/'report.json').read_text());world=json.loads((folder/'manifest.json').read_text())
    env=BorderlandEnv(world=world);history=PaidHistory();frame={'ok':True,'result':{},'observation':env.observe()}
    actions=json.loads((folder/'actions.json').read_text()) if (folder/'actions.json').exists() else []
    calls=sorted(folder.glob('call-*'),key=lambda p:int(p.name.split('-')[-1]))
    attempts=report['ledger']['attempts'];threads=set();states=set();wipes=[]
    limit=report['ledger']['limit'];assert type(limit) is int and 1<=limit<=100
    assert len(attempts)<=limit
    if (folder/'run-contract.json').exists():
        contract=json.loads((folder/'run-contract.json').read_text());assert contract['max_calls']==limit
        for path,digest in contract['source_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    for i,call in enumerate(calls):
        history.add(frame);messages=history.messages()
        assert json.loads((call/'public-messages.json').read_text())==messages
        if (call/'request.json').exists():
            raw=(call/'request.json').read_bytes();payload=json.loads(raw)
            assert payload==public_payload(messages)
            assert normalize(json.loads((call/'native-request.json').read_text()),messages)==payload
            assert hashlib.sha256(raw).hexdigest()==attempts[i]['request_sha256']
        if (call/'verified.json').exists():
            proof=json.loads((call/'verified.json').read_text())
            assert proof['state'] not in states;states.add(proof['state'])
            assert len(proof['thread_ids'])==1 and proof['thread_ids'][0] not in threads
            threads.add(proof['thread_ids'][0])
        if i>=len(actions):continue
        raw,usage=parse_sse((call/'response.sse').read_bytes());output=strict_json(raw)
        validate(output,response_schema(frame['observation']))
        action={'tool':output['tool'],'args':output['args']}
        assert raw==actions[i]['raw'] and action==actions[i]['action']
        assert canonical(frame)==canonical(actions[i]['public_frame'])
        history.act(output);step=env.step(action)
        assert canonical(step.observation)==canonical(actions[i]['output'])
        if step.info['epoch_changed']:
            assert len(env.notebook)==8 and all(len(line)<=96 and all(32<=ord(c)<=126 for c in line) for line in env.notebook)
            wipes.append({'after_action':i,'notebook':list(env.notebook)})
            history=PaidHistory();frame={'ok':True,'result':{},'observation':env.observe()}
        else:frame=step.observation
    assert env.room==report['last_room'] and env.success==report['success']
    assert wipes==[{k:w[k] for k in ['after_action','notebook']} for w in report['wipes']]
    assert canonical(env.trace)==canonical([json.loads(x) for x in (folder/'trace.jsonl').read_text().splitlines()])
    for path,digest in report['source_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    result={'all_checks_passed':True,'attempts':len(attempts),'call_limit':limit,'actions':len(actions),'last_room':env.room,
            'wipes_verified':len(wipes),
            'exact_public_payloads':True,'no_coding_tools':True,'exact_environment_replay':True,
            'unique_threads':len(threads),'unique_states':len(states),
            'bridge_source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (ROOT/'baseline/codex_subscription').glob('*.py')}}
    write(folder/'audit.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder');args=parser.parse_args();audit(ROOT/args.folder)
