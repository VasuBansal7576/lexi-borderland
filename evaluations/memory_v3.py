"""Bounded, explicitly upstream-assisted model-note/wipe component test."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.run import Server,write
from baseline.run_v3 import prepare,infer
from baseline.interface_v3 import PublicHistory,canonical,response_schema,validate
from borderland.env import BorderlandEnv


def main():
    base=ROOT/'artifacts/model-interface-v3/memory'
    base.mkdir(parents=True,exist_ok=False)
    server=Server(base);summaries=[]
    try:
        for phase,sigma in ((0,0),(0,1),(1,0),(1,1)):
            folder=base/f'p{phase}-s{sigma}';folder.mkdir()
            source=ROOT/f'artifacts/certification-v1/family-0000/phase-{phase}-sigma-{sigma}'
            env,history,frame=prepare(source,3,True)
            prefix_count=len(env.trace);calls=[];owned=[];requests=[];errors=[];raw_responses=[];schema_errors=[]
            server.start();old_pid=server.proc.pid;new_pid=None;fresh=None
            evaluator_exit=False;notebook=None;postwipe_cached=None
            write(folder/'manifest.json',env.world)
            def model_step():
                nonlocal frame,history
                history.add(frame)
                payload={'model':'tiny-aya-global-q4_k_m','messages':history.messages(),'temperature':0,'seed':42,'max_tokens':1024,
                         'response_format':{'type':'json_schema','json_schema':{'name':'borderland_action','strict':True,'schema':response_schema(frame['observation'])}}}
                requests.append({'public_frame':frame,'server_pid':server.proc.pid,'request':payload})
                write(folder/'requests.json',requests)
                response=infer(payload)
                raw_responses.append(response);write(folder/'responses.json',raw_responses)
                raw=response['choices'][0]['message'].get('content','')
                try:
                    output=json.loads(raw)
                    validate(output,response_schema(frame['observation']))
                    action={'tool':output['tool'],'args':output['args']}
                except Exception as error:
                    schema_errors.append(type(error).__name__+': '+str(error))
                    output,action={'invalid_raw_output':raw},{}
                calls.append({**requests[-1],'response':response,'action':action})
                history.act(output)
                old_room=env.room
                result=env.step(action);frame=result.observation
                owned.append({'actor':'model','action':action})
                write(folder/'calls.json',calls)
                print(f"memory-v3 p={phase} s={sigma} room={old_room} tool={action.get('tool')} ok={frame['ok']} terminal={env.reason}",flush=True)
                return result
            try:
                # Up to four unrestricted actions to read/write/exit. This cap
                # is a component protocol, never an environment rule change.
                for _ in range(4):
                    model_step()
                    if env.room==4 or env.terminated or env.truncated:break
                notebook=list(env.notebook)
                if env.room==3 and not(env.terminated or env.truncated):
                    action={'tool':'exit_room','args':{}}
                    result=env.step(action)
                    assert result.info['epoch_changed'] and result.observation['ok']
                    owned.append({'actor':'evaluator_fixed_boundary','action':action})
                    evaluator_exit=True
                if env.room==4:
                    assert env.notebook==notebook
                    server.start();new_pid=server.proc.pid
                    history=PublicHistory()
                    frame={'ok':True,'result':{},'observation':env.observe()};fresh=frame
                    first_post=len(calls)
                    for _ in range(4):
                        model_step()
                        if env.terminated or env.truncated or env.data['unlocked']:break
                    assert old_pid!=new_pid
                    postwipe_cached=calls[first_post]['response']['usage']['prompt_tokens_details']['cached_tokens']
                    assert postwipe_cached==0
                    assert len(json.loads(calls[first_post]['request']['messages'][1]['content'])['history_since_last_wipe']['events'])==1
            except Exception as error:
                errors.append(type(error).__name__+': '+str(error))
                print(f'memory-v3 p={phase} s={sigma} ERROR {errors[-1]}',flush=True)
            replay=BorderlandEnv(world=env.world)
            for row in env.trace:
                replay.step(row['action']);assert canonical(replay.trace[-1])==canonical(row)
            report={'scope':'upstream-assisted component; four model actions before fixed boundary, up to four after; evaluator exit never credited as model success',
                    'interface':'typed-v3','phase':phase,'sigma':sigma,'source':str(source.relative_to(ROOT)),
                    'prefix_actions':prefix_count,'evaluator_exit':evaluator_exit,
                    'notebook':notebook,'bytes':sum(map(len,notebook)) if notebook is not None else None,
                    'old_pid':old_pid,'new_pid':new_pid,'fresh_frame':fresh,
                    'model_calls':len(calls),'gate_passed':env.room==4 and env.data['unlocked'],
                    'reason':('inference_error' if errors else env.reason or 'component_cap_or_gate_passed'),
                    'errors':errors,'schema_errors':schema_errors,'owned_actions':owned,'exact_replay':True,'postwipe_cached_tokens':postwipe_cached,
                    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for parent in (ROOT/'baseline',ROOT/'borderland') for p in sorted(parent.glob('*.py'))}}
            write(folder/'memory-check.json',report)
            (folder/'trace.jsonl').write_text(''.join(canonical(r)+'\n' for r in env.trace))
            summaries.append({k:report[k] for k in ('phase','sigma','evaluator_exit','bytes','model_calls','gate_passed','reason','old_pid','new_pid','errors')})
            write(base/'summary.json',summaries)
    finally:server.stop()

if __name__=='__main__':main()
