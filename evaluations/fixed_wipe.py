"""Controlled memory component test, never an unassisted escape claim."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.run import Server,write
from baseline.run_v2 import prepare,infer
from baseline.interface_v2 import PublicHistory,canonical,response_schema,validate
from borderland.env import BorderlandEnv


def main():
    base=ROOT/'artifacts/model-interface-v2/fixed-wipe'
    base.mkdir(parents=True,exist_ok=False)
    server=Server(base);summaries=[]
    try:
        for phase,sigma in ((0,0),(0,1),(1,0),(1,1)):
            folder=base/f'p{phase}-s{sigma}';folder.mkdir()
            source=ROOT/f'artifacts/certification-v1/family-0000/phase-{phase}-sigma-{sigma}'
            env,history,frame=prepare(source,3,True)
            prefix_count=len(env.trace);calls=[];owned=[]
            server.start()
            def model_step():
                nonlocal frame,history
                history.add(frame)
                payload={'model':'tiny-aya-global-q4_k_m','messages':history.messages(),'temperature':0,'seed':42,'max_tokens':1024,
                         'response_format':{'type':'json_schema','json_schema':{'name':'borderland_action','strict':True,'schema':response_schema(frame['observation'])}}}
                response=infer(payload)
                raw=response['choices'][0]['message']['content'];output=json.loads(raw)
                validate(output,response_schema(frame['observation']))
                action={'tool':output['tool'],'args':output['args']}
                calls.append({'public_frame':frame,'server_pid':server.proc.pid,'request':payload,'response':response,'action':action})
                history.act(output)
                result=env.step(action);frame=result.observation
                owned.append({'actor':'model','action':action})
                write(folder/'calls.json',calls)
                print(f"fixed-wipe p={phase} s={sigma} room={env.room} tool={action['tool']} result={result.observation['result']}",flush=True)
                return result
            model_step()  # same policy interface; notebook contents never supplied
            notebook=list(env.notebook)
            old_pid=server.proc.pid
            evaluator_exit=False
            if env.room==3 and not env.terminated:
                # This is an EXPLICIT EVALUATOR ACTION in a ready room, not
                # substituted for a model action or credited as model gameplay.
                action={'tool':'exit_room','args':{}}
                result=env.step(action)
                assert result.info['epoch_changed'] and result.observation['ok']
                owned.append({'actor':'evaluator_fixed_boundary','action':action})
                evaluator_exit=True
            assert env.room==4 and env.notebook==notebook
            server.start();new_pid=server.proc.pid
            history=PublicHistory()
            frame={'ok':True,'result':{},'observation':env.observe()}
            fresh=frame
            for _ in range(4):
                model_step()
                if env.terminated or env.truncated or env.data['unlocked']:break
            assert old_pid!=new_pid
            assert calls[1]['response']['usage']['prompt_tokens_details']['cached_tokens']==0
            assert len(json.loads(calls[1]['request']['messages'][1]['content'])['history_since_last_wipe']['events'])==1
            replay=BorderlandEnv(world=env.world)
            for row in env.trace:
                replay.step(row['action']);assert canonical(replay.trace[-1])==canonical(row)
            report={'scope':'controlled upstream-assisted memory probe; evaluator may perform the already-legal room3 exit; never an unassisted success',
                    'phase':phase,'sigma':sigma,'source':str(source.relative_to(ROOT)),'prefix_actions':prefix_count,
                    'evaluator_exit':evaluator_exit,'notebook':notebook,'bytes':sum(map(len,notebook)),
                    'old_pid':old_pid,'new_pid':new_pid,'fresh_frame':fresh,
                    'model_calls':len(calls),'model_actions':[c['action'] for c in calls],
                    'gate_passed':env.data['unlocked'],'reason':env.reason or 'probe_step_cap_or_gate_passed',
                    'owned_actions':owned,'exact_replay':True,
                    'postwipe_cached_tokens':calls[1]['response']['usage']['prompt_tokens_details']['cached_tokens'],
                    'adapter_sha256':hashlib.sha256((ROOT/'baseline/interface_v2.py').read_bytes()).hexdigest()}
            write(folder/'memory-check.json',report);write(folder/'manifest.json',env.world)
            (folder/'trace.jsonl').write_text(''.join(canonical(r)+'\n' for r in env.trace))
            summaries.append({k:report[k] for k in ('phase','sigma','evaluator_exit','bytes','model_calls','gate_passed','reason','old_pid','new_pid')})
            write(base/'summary.json',summaries)
    finally:server.stop()

if __name__=='__main__':main()
