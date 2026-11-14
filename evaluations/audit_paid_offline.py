"""Replay the saved offline fixture and reconstruct every outward request."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.paid.config import Config
from baseline.paid.run import PaidHistory
from baseline.paid.guard import LoopGuard
from baseline.paid.client import strict_json
from baseline.interface_v3 import canonical,response_schema,validate
from borderland.env import BorderlandEnv

BASE=ROOT/'artifacts/paid-adapter-offline/proof'


def audit(folder):
    report=json.loads((folder/'report.json').read_text())
    assert report['mode']=='offline_scripted_fixture_not_model'
    ledger=report['ledger'];config=Config(**ledger['contract'])
    env=BorderlandEnv(world=json.loads((folder/'manifest.json').read_text()))
    events=[json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
    requests=[event for event in events if event['kind']=='request']
    responses=[event for event in events if event['kind']=='response']
    actions=json.loads((folder/'actions.json').read_text()) if (folder/'actions.json').exists() else []
    assert len(requests)==len(responses)==len(actions)==ledger['calls']
    history=PaidHistory();guard=LoopGuard(config.no_progress_limit)
    frame={'ok':True,'result':{},'observation':env.observe()}
    spent=Decimal(0);inputs=outputs=0;wipe_count=0
    for i,(request,response,action,entry) in enumerate(zip(requests,responses,actions,ledger['entries'])):
        assert request['request_id']==response['request_id']==entry['request_id']
        assert i+1<=config.max_calls and inputs+config.context_window<=config.max_input_tokens
        assert outputs+config.output_tokens_per_call<=config.max_output_tokens
        assert spent+config.reservation<=Decimal(config.budget_usd)
        history.add(frame)
        expected={'model':config.model,'messages':history.messages(),'n':1,'stream':False,'store':False,
                  config.output_limit_field:config.output_tokens_per_call,'response_format':{'type':'json_object'}}
        assert request['payload']==expected,'private data, injected answer, or altered prompt'
        assert canonical(action['public_frame'])==canonical(frame)
        value=response['response'];usage=value['usage']
        raw=value['choices'][0]['message']['content'];output=strict_json(raw)
        validate(output,response_schema(frame['observation']))
        actual={'tool':output['tool'],'args':output['args']}
        assert actual==action['action'] and raw==action['raw']
        assert usage['prompt_tokens']==entry['inputs'] and usage['completion_tokens']==entry['outputs']
        inputs+=entry['inputs'];outputs+=entry['outputs'];spent+=config.cost(entry['inputs'],entry['outputs'])
        history.act(output);before=frame
        step=env.step(actual)
        assert canonical(step.observation)==canonical(action['output'])
        if step.info['epoch_changed']:
            boundary=report['wipes'][wipe_count];wipe_count+=1
            assert boundary['notebook']==env.notebook and boundary['after_action']==i
            assert len(env.notebook)==8 and all(len(s)<=96 and all(32<=ord(c)<=126 for c in s) for s in env.notebook)
            history=PaidHistory();guard=LoopGuard(config.no_progress_limit)
            frame={'ok':True,'result':{},'observation':env.observe()}
            assert canonical(boundary['fresh_frame'])==canonical(frame)
        else:
            frame=step.observation
            if guard.observe(before,actual,frame) and not(env.terminated or env.truncated):
                assert i==len(actions)-1 and report['stop']=='evaluator_no_progress'
    trace=[json.loads(line) for line in (folder/'trace.jsonl').read_text().splitlines()]
    assert canonical(env.trace)==canonical(trace)
    assert env.score==report['score'] and env.success==report['success']
    assert env.reason==report['environment_reason'] and wipe_count==len(report['wipes'])
    assert inputs==ledger['input_tokens_accounted'] and outputs==ledger['output_tokens_accounted']
    assert spent==Decimal(ledger['cost_accounted_usd']) and spent<=Decimal(config.budget_usd)
    for path,digest in report['source_hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    return {'case':folder.name,'fake_requests':len(requests),'wipes':wipe_count,
            'public_only_requests':True,'no_action_repair':True,'exact_replay':True,
            'budget_admission_verified':True,'source_hashes_match':True}


def main():
    results=[audit(path.parent) for path in sorted(BASE.glob('*/report.json'))]
    assert len(results)==3
    report={'all_checks_passed':True,'cases':results,'actual_model_performance_claimed':False}
    (BASE.parent/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
