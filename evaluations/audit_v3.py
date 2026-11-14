"""Reconstruct model-visible requests from authoritative legal transitions."""
import hashlib
import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.interface_v3 import PublicHistory, SYSTEM, canonical, response_schema, unpack
from baseline.interface_v2 import valid
from baseline.run_v3 import prepare
from borderland.env import BorderlandEnv

BASE=ROOT/'artifacts/model-interface-v3'


def lines(path):return [json.loads(x) for x in path.read_text().splitlines()]


def audit(folder):
    report=json.loads((folder/'report.json').read_text())
    prefix=json.loads((folder/'prefix.json').read_text())
    env,history,frame=prepare(ROOT/prefix['source'],report['start_room'],report['notebook_probe'])
    assert len(env.trace)==prefix['reference_actions']
    requests,responses,actions=map(lines,(folder/'requests.jsonl',folder/'responses.jsonl',folder/'actions.jsonl'))
    assert len(actions)==len(responses)==report['model_calls']
    schemas_invalid=0
    wipe_by_index={w['after_request']+1:w for w in report['wipes']}
    for i,record in enumerate(requests):
        assert canonical(record['public_frame'])==canonical(frame)
        history.add(frame)
        expected=history.messages()
        actual_messages=record['request']['messages']
        assert actual_messages==expected, 'unexpected context, ordering change, or leaked answer'
        assert record['request']['response_format']['json_schema']['schema']==response_schema(frame['observation'])
        reconstructed=unpack(json.loads(expected[1]['content'])['history_since_last_wipe'])
        original=json.loads(json.dumps(history.frames))
        for v in original:v['observation'].pop('tools')
        assert reconstructed==original
        if i in wipe_by_index:
            wipe=wipe_by_index[i]
            assert wipe['old_pid']!=wipe['new_pid']==record['server_pid']
            assert frame==wipe['fresh_frame']
            assert history.actions==[] and len(history.frames)==1
            assert len(wipe['notebook'])==8 and all(len(x)<=96 for x in wipe['notebook'])
            if i<len(responses):assert responses[i]['usage']['prompt_tokens_details']['cached_tokens']==0
        if i==len(responses):break  # recorded inference error, no fabricated action
        raw=responses[i]['choices'][0]['message']['content']
        assert raw==actions[i]['raw']
        try:
            output=json.loads(raw)
            conforms=valid(output,response_schema(frame['observation']))
        except ValueError:
            conforms=False
        if conforms:
            action={'tool':output['tool'],'args':output['args']}
        else:
            output,action={'invalid_raw_output':raw},{}
            schemas_invalid+=1
        assert action==actions[i]['action'], 'action repair or substitution'
        history.act(output)
        result=env.step(action)
        assert canonical(result.observation)==canonical(actions[i]['output'])
        if result.info['epoch_changed']:
            history=PublicHistory()
            frame={'ok':True,'result':{},'observation':env.observe()}
        else:frame=result.observation
    assert canonical(env.trace)==canonical(lines(folder/'trace.jsonl'))
    assert env.score==report['score_including_prefix'] and env.success==report['success']
    for relative,expected_hash in report['source_hashes'].items():
        candidates=[ROOT/relative,BASE/'source-initial'/relative,BASE/'source-json-normalization'/relative,BASE/'source-before-entry-wording'/relative]
        assert any(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==expected_hash for p in candidates),relative
    tool_counts=Counter(a['action'].get('tool','invalid') for a in actions)
    result={k:report[k] for k in ('name','success','assisted_prefix','notebook_probe','reason','last_room','rooms_completed_from_entry','model_calls','protocol_errors','completion_tokens','wipes','errors')}
    result.update(schema_violations=schemas_invalid,tool_counts=dict(tool_counts),
                  model_records_read=[a['action']['args']['record_id'] for a in actions if a['action'].get('tool')=='read_record' and a['output']['ok']],
                  maximum_prompt_tokens=max((r['usage']['prompt_tokens'] for r in responses),default=0),
                  exact_replay=True,public_only_transport=True,artifact=str(folder.relative_to(BASE)))
    if actions:
        result['last_action']=actions[-1]['action']
        result['last_public_state']=actions[-1]['output']['observation']
    return result,actions


def main():
    runs,raw=[],[]
    for path in sorted(BASE.glob('*/*/report.json')):
        row,actions=audit(path.parent)
        runs.append(row);raw.append((row,actions))
    result={'runs':runs,'unassisted_attempts':sum(not r['assisted_prefix'] for r in runs),
            'unassisted_escapes':sum(r['success'] for r in runs if not r['assisted_prefix']),
            'model_actions':sum(r['model_calls'] for r in runs),
            'schema_violations':sum(r['schema_violations'] for r in runs),
            'all_public_transport_and_replay_checks_passed':True}
    (BASE/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    page=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Tiny Aya typed-interface rerun</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:20px;background:#101820;color:#e8eef5}summary{cursor:pointer;padding:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#1e2a38;padding:15px;border-radius:8px}p{line-height:1.6;color:#b7c9dc}details{border:1px solid #44556b;border-radius:8px;margin:12px 0}</style><h1>Tiny Aya · typed-interface rerun</h1><p>Actual model outputs. Unassisted episodes and reference-prefix diagnostics are labeled separately. No action repair or answer injection.</p>']
    for row,actions in raw:
        label=f"{row['name']} · {'ASSISTED' if row['assisted_prefix'] else 'UNASSISTED'} · {row['reason']} · {row['model_calls']} calls"
        page.append('<details><summary>'+html.escape(label)+'</summary>')
        if row['wipes']:page.append('<h3>Actual wipe</h3><pre>'+html.escape(json.dumps(row['wipes'],indent=2))+'</pre>')
        for a in actions:
            page.append('<details><summary>'+html.escape(f"Action {a['index']+1} · room {a['room']} · {a['action'].get('tool','invalid')}")+'</summary><pre>'+html.escape(a['raw'])+'</pre><pre>'+html.escape(json.dumps(a['output'],indent=2))+'</pre></details>')
        page.append('</details>')
    page.append('</html>')
    (BASE/'viewer.html').write_text('\n'.join(page))
    print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))


if __name__=='__main__':main()
