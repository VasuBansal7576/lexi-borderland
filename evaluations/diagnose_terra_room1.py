"""Post-run diagnostic from delivered public records; never used by a live policy."""
import itertools,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/codex-terra-episode-v1'

def main():
    actions=json.loads((BASE/'live/actions.json').read_text())
    records={}
    for row in actions:
        result=row['output']['result']
        if 'text' in result:
            record=json.loads(result['text'])
            if record.get('epoch')=='current':records[record['kind']]=record
    phases=[p for p in range(4) if all((s['wall']+p)%4==s['district_mod4']
                                     for s in records['clock_pairs']['samples'])]
    assert phases==[0]
    constraints=records['glyph_constraints'];glyph,offset=constraints['phase_anchor']
    interpretations={}
    for name,sign in [('first_minus_second',1),('second_minus_first',-1)]:
        solutions=[]
        for values in itertools.permutations(range(4)):
            mapping=dict(zip('ABCD',values))
            if (mapping[glyph]-phases[0])%4!=offset:continue
            if all(sign*(mapping[a]-mapping[b])%4==d for a,b,d in constraints['differences']):solutions.append(mapping)
        assert len(solutions)==1
        interpretations[name]={'mapping':solutions[0],'door_predictions':[]}
        for index in [6,7]:
            obs=actions[index]['public_frame']['observation']
            sector=(phases[0]+obs['bank']+obs['pulse'])%4
            door=next(k for k,v in solutions[0].items() if v==sector)
            interpretations[name]['door_predictions'].append({'call':index+1,'bank':obs['bank'],'pulse':obs['pulse'],
                'sector':sector,'predicted_door':door,'model_door':actions[index]['action']['args']['door_id']})
    assert interpretations['first_minus_second']['door_predictions'][0]['predicted_door']==actions[6]['action']['args']['door_id']
    assert interpretations['second_minus_first']['door_predictions'][1]['predicted_door']==actions[7]['action']['args']['door_id']
    assert interpretations['first_minus_second']['door_predictions'][1]['predicted_door']!=actions[7]['action']['args']['door_id']
    result={'inputs':'saved public observations and fully delivered records only','live_calls':0,
        'phase_candidates':phases,'interpretations':interpretations,
        'model_rationales':[json.loads(actions[i]['raw'])['reason'] for i in [6,7]],
        'implemented_convention':'first_minus_second',
        'convention_source':'Evaluator inspection of borderland/world.py and borderland/solver.py after the run; not supplied to the model.',
        'finding':'The model used the reverse subtraction direction. The public record encoding does not explicitly define that direction; the first door does not distinguish the two interpretations.',
        'classification':'terminal puzzle failure confounded by an implicit record-encoding convention; not a memory result'}
    (BASE/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
