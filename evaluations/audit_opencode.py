"""Independent reconstruction of all legal evidence sent through the OpenCode bridge."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.paid.run import PaidHistory
from baseline.paid.client import strict_json
from baseline.interface_v3 import validate,response_schema,canonical
from baseline.opencode_free.bridge import validate_payload,parse_stream,MODELS,write
from borderland.env import BorderlandEnv


def audit(base):
    results=[];sessions=set();states=set()
    for model in MODELS:
        folder=base/model
        if not (folder/'report.json').exists():continue
        report=json.loads((folder/'report.json').read_text())
        env=BorderlandEnv(world=json.loads((folder/'manifest.json').read_text()))
        history=PaidHistory();frame={'ok':True,'result':{},'observation':env.observe()}
        actions=json.loads((folder/'actions.json').read_text()) if (folder/'actions.json').exists() else []
        calls=sorted(folder.glob('call-*'))
        attempts=[r for r in report['ledger']['attempts'] if r['model']==model]
        assert len(attempts)<=5 and len(report['ledger']['attempts'])<=25
        for attempt in attempts:
            assert attempt['request_sha256'] in [hashlib.sha256((p/'request.json').read_bytes()).hexdigest()
                                                 for p in calls if (p/'request.json').exists()]
        for i,call in enumerate(calls):
            history.add(frame);messages=history.messages()
            assert json.loads((call/'public-messages.json').read_text())==messages
            if (call/'request.json').exists():
                validate_payload(json.loads((call/'request.json').read_text()),model,messages)
            if (call/'verified.json').exists():
                verified=json.loads((call/'verified.json').read_text())
                assert verified['fresh_state'] not in states;states.add(verified['fresh_state'])
                assert len(verified['session_ids'])==1
                session=verified['session_ids'][0];assert session not in sessions;sessions.add(session)
            if i>=len(actions):continue
            raw,_=parse_stream((call/'response.sse').read_bytes(),model)
            output=strict_json(raw);validate(output,response_schema(frame['observation']))
            actual={'tool':output['tool'],'args':output['args']}
            assert raw==actions[i]['raw'] and actual==actions[i]['action']
            assert canonical(frame)==canonical(actions[i]['public_frame'])
            history.act(output);step=env.step(actual)
            assert canonical(step.observation)==canonical(actions[i]['output'])
            if step.info['epoch_changed']:
                history=PaidHistory();frame={'ok':True,'result':{},'observation':env.observe()}
            else:frame=step.observation
        assert len(calls)<=5 and len(actions)<=len(calls)
        assert env.room==report['last_room'] and env.success==report['success'] and env.score==report['score']
        assert canonical(env.trace)==canonical([json.loads(x) for x in (folder/'trace.jsonl').read_text().splitlines()])
        for path,digest in report['source_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
        results.append({'model':model,'client_calls':len(calls),'upstream_attempts':len(attempts),'actions':len(actions),'last_room':env.room,
                        'exact_public_messages':True,'unchanged_environment_replay':True})
    result={'all_checks_passed':True,'models':results,'unique_verified_sessions':len(sessions),
            'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((ROOT/'baseline/opencode_free').glob('*.py'))}}
    write(base/'audit.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder');args=parser.parse_args()
    print(json.dumps(audit(ROOT/args.folder),indent=2))
