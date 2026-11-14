"""Independent transport replay for the bounded, assisted memory components."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.interface_v2 import valid
from baseline.run_v3 import prepare
from baseline.interface_v3 import PublicHistory,canonical,response_schema,validate,unpack
BASE=ROOT/'artifacts/model-interface-v3/memory'


def audit(folder):
    report=json.loads((folder/'memory-check.json').read_text())
    starts=json.loads((BASE/'server-starts.json').read_text())
    pids={s['pid'] for s in starts}
    assert report['old_pid'] in pids
    env,history,frame=prepare(ROOT/report['source'],3,True)
    assert len(env.trace)==report['prefix_actions']
    calls=json.loads((folder/'calls.json').read_text()) if (folder/'calls.json').exists() else []
    requests=json.loads((folder/'requests.json').read_text())
    assert len(calls)==report['model_calls']
    index=0;wiped=False;first_post=True;model_pre=0;model_post=0;eval_exits=0
    for owned in report['owned_actions']:
        if owned['actor']=='model':
            call=calls[index]
            assert call['request']==requests[index]['request']
            assert canonical(frame)==canonical(call['public_frame'])
            history.add(frame)
            assert call['request']['messages']==history.messages(), 'extra information in prompt'
            assert call['request']['response_format']['json_schema']['schema']==response_schema(frame['observation'])
            expected=json.loads(json.dumps(history.frames))
            for f in expected:f['observation'].pop('tools')
            assert unpack(history.pack())==expected
            if wiped:
                model_post+=1
                assert call['server_pid']==report['new_pid']!=report['old_pid']
                if first_post:
                    assert len(history.frames)==1 and history.actions==[]
                    assert call['response']['usage']['prompt_tokens_details']['cached_tokens']==0
                    assert canonical(frame)==canonical(report['fresh_frame'])
                    assert frame['observation']['notebook']==report['notebook']
                    first_post=False
            else:
                model_pre+=1
                assert call['server_pid']==report['old_pid']
            raw=call['response']['choices'][0]['message'].get('content','')
            try:
                output=json.loads(raw)
                validate(output,response_schema(frame['observation']))
                action={'tool':output['tool'],'args':output['args']}
            except Exception:
                output,action={'invalid_raw_output':raw},{}
            assert action==call['action']==owned['action'], 'action substitution'
            history.act(output);index+=1
        else:
            assert owned['actor']=='evaluator_fixed_boundary'
            assert not wiped and env.room==3 and model_pre==4
            action=owned['action']
            assert action=={'tool':'exit_room','args':{}}
            eval_exits+=1
        before=list(env.notebook)
        result=env.step(action)
        if result.info['epoch_changed']:
            assert result.observation['ok'] and before==env.notebook==report['notebook']
            wiped=True
            history=PublicHistory();frame={'ok':True,'result':{},'observation':env.observe()}
            if report['new_pid'] is not None:
                assert report['new_pid'] in pids and report['new_pid']!=report['old_pid']
                assert canonical(frame)==canonical(report['fresh_frame'])
        else:frame=result.observation
    assert index==len(calls)
    assert model_pre<=4 and model_post<=4 and eval_exits==int(report['evaluator_exit'])
    if len(requests)>len(calls):
        assert len(requests)==len(calls)+1 and report['errors']
        history.add(frame)
        assert requests[-1]['request']['messages']==history.messages()
        assert canonical(requests[-1]['public_frame'])==canonical(frame)
    trace=[json.loads(x) for x in (folder/'trace.jsonl').read_text().splitlines()]
    assert canonical(env.trace)==canonical(trace)
    assert report['gate_passed']==(env.room==4 and env.data['unlocked'])
    for name,digest in report['source_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    if wiped:
        assert len(report['notebook'])==8
        assert all(len(s)<=96 and all(32<=ord(c)<=126 for c in s) for s in report['notebook'])
    return {'case':folder.name,'model_actions':len(calls),'model_pre':model_pre,'model_post':model_post,
            'real_wipe':wiped and report['new_pid'] is not None,'evaluator_exit':report['evaluator_exit'],
            'gate_passed':report['gate_passed'],'errors':report['errors'],
            'exact_replay':True,'public_transport_only':True,'no_action_repair':True,
            'notebook_only_transfer':wiped,'notebook_bytes':report['bytes']}


def main():
    results=[audit(path.parent) for path in sorted(BASE.glob('*/memory-check.json'))]
    report={'cases':results,'all_checks_passed':True}
    (BASE/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
