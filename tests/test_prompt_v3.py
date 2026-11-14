import copy
import json
import unittest
from itertools import product
from baseline.interface_v3 import PublicHistory, canonical, response_schema, unpack
from baseline.run_v3 import prepare, ROOT


class PromptV3Tests(unittest.TestCase):
    def test_current_room_request_and_complete_evidence(self):
        source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
        for room in range(1,8):
            env,history,frame=prepare(source,room)
            history.add(frame)
            message=json.loads(history.messages()[1]['content'])
            self.assertIn(f'room {room}:',message['instruction'])
            if room==3:self.assertIn('Before exiting this room',message['respond_now'])
            else:self.assertNotIn('Before exiting this room',message['respond_now'])
            original=copy.deepcopy(history.frames)
            for value in original:value['observation'].pop('tools')
            self.assertEqual(unpack(message['history_since_last_wipe']),original)
            self.assertEqual(list(message['history_since_last_wipe']),['events','public_room_rules','results'])

    def test_blank_notebook_wipe_prompts_identical_across_twins(self):
        messages=[];schemas=[]
        for phase,sigma in product(range(2),repeat=2):
            source=ROOT/f'artifacts/certification-v1/family-0000/phase-{phase}-sigma-{sigma}'
            env,history,frame=prepare(source,4)
            frame['observation']['notebook']=['']*8
            history.add(frame)
            messages.append(canonical(history.messages()))
            schemas.append(canonical(response_schema(frame['observation'])))
            self.assertEqual(len(history.frames),1)
            self.assertEqual(history.actions,[])
        self.assertEqual(len(set(messages)),1)
        self.assertEqual(len(set(schemas)),1)

    def test_evidence_in_history_distinguished_from_notebook(self):
        source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
        env,history,frame=prepare(source,3,True)
        history.add(frame)
        self.assertEqual(frame['observation']['notebook'],['']*8)
        message=json.loads(history.messages()[1]['content'])
        self.assertTrue(any('canonical_json_text' in value['result'] for value in message['history_since_last_wipe']['results']))
        self.assertIn('empty notebook does NOT mean',history.messages()[0]['content'])


if __name__=='__main__':unittest.main()
