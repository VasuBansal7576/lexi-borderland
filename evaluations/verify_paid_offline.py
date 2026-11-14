"""Saved proof of adapter plumbing only; socket I/O forbidden, no actual model."""
import copy
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.paid.config import Config
from baseline.paid.budget import Ledger
from baseline.paid.client import Client
from baseline.paid.run import EventLog, run_episode
from borderland.env import BorderlandEnv


class ScriptedFixture:
    def __init__(self, actions):
        self.actions=iter(actions)
        self.requests=[]
    def send(self,payload,request_id):
        self.requests.append(copy.deepcopy(payload))
        action=next(self.actions)
        return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'reason':'OFFLINE SCRIPTED FIXTURE, NOT A MODEL',**action})}}],
                'usage':{'prompt_tokens':100,'completion_tokens':30,'total_tokens':130}}


def main():
    base=ROOT/'artifacts/paid-adapter-offline/proof'
    base.mkdir(parents=True,exist_ok=False)
    source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
    world=json.loads((source/'manifest.json').read_text())
    witness=[json.loads(line)['action'] for line in (source/'trace.jsonl').read_text().splitlines()]
    default=Config.read('baseline/paid/offline-example.json')
    cases=[('loop',default,[{'tool':'inspect','args':{'object_id':'rules'}}]*10),
           ('budget',replace(default,budget_usd='0.01'),witness),
           ('all-seven-scripted',replace(default,max_calls=160,max_input_tokens=3000000,
                                        max_output_tokens=30000,budget_usd='10'),witness)]
    rows=[]
    with ExitStack() as stack:
        sockets=[stack.enter_context(patch(name,side_effect=AssertionError('NETWORK FORBIDDEN'))) for name in
                 ('socket.socket.connect','socket.socket.connect_ex','socket.socket.sendto','socket.create_connection','socket.getaddrinfo')]
        for name,config,actions in cases:
            folder=base/name;folder.mkdir()
            ledger=Ledger(config,base/(name+'-ledger.json'));log=EventLog(folder/'events.jsonl')
            fixture=ScriptedFixture(actions)
            try:
                report=run_episode(BorderlandEnv(world=world),Client(config,ledger,fixture,log),folder,
                                   mode='offline_scripted_fixture_not_model')
                rows.append({'name':name,'fake_requests':len(fixture.requests),'actions':report['actions'],
                             'stop':report['stop'],'fixture_success':report['success'],'wipes':len(report['wipes'])})
            finally:log.close();ledger.close()
        assert all(mock.call_count==0 for mock in sockets)
    assert rows[0]['fake_requests']==4 and rows[0]['stop']=='evaluator_no_progress'
    assert rows[1]['fake_requests']==0 and rows[1]['stop']=='dollar_budget'
    assert rows[2]['fixture_success'] and rows[2]['wipes']==1
    summary={'actual_network_calls':0,'actual_paid_spend_usd':'0','actual_model_calls':0,
             'model_success_measured':False,'cases':rows,
             'note':'The full-room fixture replays known legal actions ONLY as fake provider responses; it is not model performance.'}
    (base/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
