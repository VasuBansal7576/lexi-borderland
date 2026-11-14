import copy
import json
import unittest
from itertools import product

from baseline.interface_v2 import PARAMETERS, PublicHistory, canonical, response_schema, unpack, valid
from baseline.run_v2 import prepare, ROOT
from borderland.env import BorderlandEnv, SIGNATURES, TRAPS


class TypedInterfaceTests(unittest.TestCase):
    def test_reference_memory_prefix_roundtrips_as_actual_json_wire(self):
        source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
        env,history,frame=prepare(source,3,True)
        history.add(frame)
        expected=json.loads(json.dumps(history.frames))
        for value in expected:value['observation'].pop('tools')
        self.assertEqual(unpack(history.pack()),expected)
        probe=next(f['result'] for f in history.frames if 'signed_current' in f['result'])
        self.assertIsInstance(probe['output'],list)

    def test_every_tool_keeps_exact_argument_names(self):
        self.assertEqual(set(PARAMETERS),set(SIGNATURES))
        for name, schema in PARAMETERS.items():
            self.assertEqual(set(schema['properties']),set(SIGNATURES[name]),name)
            self.assertFalse(schema['additionalProperties'])

    def test_rejects_observed_old_protocol_failures(self):
        cases=[('submit_bid',{'bid':15}),('submit_bid',{'value':'15'}),
               ('energize',{'bus_id':'auxiliary|main'}),('move',{'destination_id':'exit'}),
               ('inspect',{'junction_id':'exit'}),('accuse',{'person_id':'V'}),
               ('unlock',{'route':True,'badge':False})]
        for tool,args in cases:self.assertFalse(valid(args,PARAMETERS[tool]),(tool,args))

    def test_notebook_exact_eight_ascii_lines(self):
        for lines in (['x'*96]*8,['']*8):self.assertTrue(valid({'lines':lines},PARAMETERS['notebook_write']))
        for lines in (['x']*7,['x']*9,['x'*97]+['']*7,['é']+['']*7,['\n']+['']*7):
            self.assertFalse(valid({'lines':lines},PARAMETERS['notebook_write']))

    def test_keeps_wrong_answers_and_both_traps_available(self):
        obs=BorderlandEnv(0).observe()
        for door in 'ABCD':self.assertTrue(valid({'reason':'test','tool':'choose_door','args':{'door_id':door}},response_schema(obs)))
        for route,badge in product(range(2),repeat=2):self.assertTrue(valid({'route':route,'badge':badge},PARAMETERS['unlock']))
        for bid in range(21):self.assertTrue(valid({'value':bid},PARAMETERS['submit_bid']))
        source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
        env,_,_=prepare(source,4)
        for tool in TRAPS:self.assertTrue(valid({'reason':'test','tool':tool,'args':{}},response_schema(env.observe())))

    def test_reference_witness_actions_not_excluded_and_history_roundtrips(self):
        source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
        env=BorderlandEnv(world=json.loads((source/'manifest.json').read_text()))
        history=PublicHistory()
        frame={'ok':True,'result':{},'observation':env.observe()}
        for line in (source/'trace.jsonl').read_text().splitlines():
            row=json.loads(line)
            action={'reason':'legal reference action',**row['action']}
            self.assertTrue(valid(action,response_schema(frame['observation'])),action)
            history.add(frame)
            expected=copy.deepcopy(history.frames)
            for x in expected:x['observation'].pop('tools')
            self.assertEqual(unpack(history.pack()),expected)
            history.act(action)
            result=env.step(row['action'])
            if result.info['epoch_changed']:
                history=PublicHistory()
                frame={'ok':True,'result':{},'observation':env.observe()}
            else:frame=result.observation

    def test_seal_projection_and_schema_independent_of_hidden_answers(self):
        source=ROOT/'artifacts/certification-v1/family-0000'
        messages,schemas=[],[]
        for p,s in product(range(2),repeat=2):
            env,history,frame=prepare(source/f'phase-{p}-sigma-{s}',4)
            frame['observation']['notebook']=['']*8
            history.add(frame)
            self.assertEqual(len(history.frames),1)
            self.assertEqual(history.actions,[])
            messages.append(canonical(history.messages()))
            schemas.append(canonical(response_schema(frame['observation'])))
        self.assertEqual(len(set(messages)),1)
        self.assertEqual(len(set(schemas)),1)

    def test_repeated_transitions_compress_without_discarding_evidence(self):
        env=BorderlandEnv(0);history=PublicHistory()
        frame={'ok':True,'result':{},'observation':env.observe()}
        for _ in range(12):
            history.add(frame)
            history.act({'reason':'status','tool':'status','args':{}})
            frame=env.step({'tool':'status','args':{}}).observation
        packed=history.pack()
        self.assertLess(len(packed['events']),len(history.frames))
        self.assertEqual(len(unpack(packed)),12)


if __name__=='__main__':unittest.main()
