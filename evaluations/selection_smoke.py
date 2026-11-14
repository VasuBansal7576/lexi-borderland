"""Synthetic free tool-selection tests; never supply gameplay answers."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.run import Server,write
from baseline.run_v3 import infer
from baseline.interface_v2 import tools_for,response_schema,validate


def main():
    base=ROOT/'artifacts/model-interface-v3/selection-smoke';base.mkdir(exist_ok=False)
    server=Server(base);rows=[]
    obs={'tools':dict.fromkeys(('status','inspect','read_record','notebook_read','notebook_write','exit_room','choose_door'))}
    cases=[('read_record',{'record_id':'synthetic-17','offset':0},'Read the catalog record synthetic-17 starting at offset0.'),
           ('choose_door',{'door_id':'B'},'This is a synthetic command-following check, not a game. Call choose_door with door_id B.'),
           ('notebook_read',{},'Read the notebook using notebook_read.'),
           ('exit_room',{},'This is a synthetic command-following check, not a game. Call exit_room with no arguments.')]
    try:
        server.start()
        for expected,args,instruction in cases:
            payload={'model':'tiny-aya-global-q4_k_m','messages':[
                {'role':'system','content':'Synthetic tool-interface test. Return one JSON object with reason, tool, args. Available tools: '+json.dumps(tools_for(obs))},
                {'role':'user','content':instruction}], 'temperature':0,'seed':42,'max_tokens':1024,
                'response_format':{'type':'json_schema','json_schema':{'name':'borderland_action','strict':True,'schema':response_schema(obs)}}}
            response=infer(payload)
            output=json.loads(response['choices'][0]['message']['content']);validate(output,response_schema(obs))
            row={'request':payload,'response':response,'expected_tool':expected,'expected_args':args,
                 'correct_selection':output['tool']==expected and output['args']==args,'schema_valid':True}
            rows.append(row);write(base/'results.json',rows)
            print(json.dumps({k:row[k] for k in ('expected_tool','correct_selection','schema_valid')}),flush=True)
    finally:server.stop()

if __name__=='__main__':main()
