"""Post-run arithmetic audit using only records, probe outputs and visible switches."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/codex-terra-notation-v1'

def main():
    actions=json.loads((BASE/'live/actions.json').read_text())
    room2=[(i+1,row) for i,row in enumerate(actions) if row['public_frame']['observation']['room']==2]
    record=next(json.loads(row['output']['result']['text']) for _,row in room2 if row['action']['tool']=='read_record')
    probes=[row for _,row in room2 if row['action']['tool']=='probe']
    channels=record['channel_glyphs']
    def output(matrix,phase,switches):
        x=[int(switches.get(g,False)) for g in channels]
        bias=[phase&1,(phase>>1)&1,(phase&1)^((phase>>1)&1)]
        return [sum(a*b for a,b in zip(row,x))%2^b for row,b in zip(matrix,bias)]
    candidates=[]
    for index,matrix in enumerate(record['matrices']):
        for phase in range(4):
            if all(output(matrix,phase,{r['action']['args']['channel_id']:r['action']['args']['setting']})==r['output']['result']['output'] for r in probes):
                candidates.append((index,phase))
    assert candidates==[(1,0)]
    index,phase=candidates[0];matrix=record['matrices'][index];rows=[]
    for call,row in room2:
        action=row['action'];obs=row['public_frame']['observation']
        if action['tool'] in ['set_switch','energize']:
            switches=dict(obs['switches'])
            if action['tool']=='set_switch':switches[action['args']['channel_id']]=action['args']['value']
            rows.append({'call':call,'action':action,'switches':switches,'calculated_output':output(matrix,phase,switches),
                'model_reason':json.loads(row['raw'])['reason'],'environment_result':row['output']['result']})
    assert rows[-1]['calculated_output']==[0,1,0]
    assert record['main_target']==[1,1,0]
    assert rows[-1]['action']=={'tool':'energize','args':{'bus_id':'main'}}
    result={'live_calls':0,'source':'Delivered schematic, both observed probes, current switches and fixed Boolean algebra only; no hidden manifest or solver.',
        'matrix_candidates_after_both_probes':len(candidates),'selected_matrix_index_zero_based':index,'inferred_phase':phase,
        'matrix':matrix,'column_order':channels,'main_target':record['main_target'],'arithmetic_trace':rows,
        'final_bit_equations':['(1*1 + 0*1 + 1*1) mod 2 = 0','(0*1 + 1*1 + 0*1) mod 2 = 1','(0*1 + 1*1 + 1*1) mod 2 = 0'],
        'finding':'Correct matrix and zero bias inferred, but the model failed to toggle the first output bit when adding D to A+C. It predicted [1,1,0] instead of [0,1,0], then energized the main bus.',
        'classification':'Public-evidence circuit arithmetic failure before the memory wipe'}
    (BASE/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['matrix_candidates_after_both_probes','column_order','main_target','finding','classification']},indent=2))

if __name__=='__main__':main()
