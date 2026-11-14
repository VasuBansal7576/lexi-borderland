import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from baseline.opencode_free.bridge import (BASE, MODELS, OUTPUT_CAP, Ledger,
    validate_payload, config_for, isolated_env, parse_stream, fake_response, sandbox_profile)
from baseline.paid.budget import BudgetStop


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=BASE)
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.messages = [{'role':'system','content':'public laws'}, {'role':'user','content':'public evidence'}]
        self.model = MODELS[0]
        self.payload = {'model':self.model,'messages':self.messages,'tools':[], 'tool_choice':'none',
                        'stream':True,'stream_options':{'include_usage':True},'max_completion_tokens':OUTPUT_CAP}

    def ledger(self):
        ledger=Ledger(self.path/'ledger.json');self.addCleanup(ledger.close);return ledger

    def test_exact_public_payload(self): validate_payload(self.payload,self.model,self.messages)

    def test_no_paid_alias_fallback_or_payload_extras(self):
        for key,value in [('model','glm-5.3-flash'),('tools',[{'name':'read'}]),
                          ('messages',self.messages+[{'role':'system','content':'hidden answer'}]),
                          ('max_completion_tokens',131072),('max_tokens',131072),
                          ('previous_response_id','old'),('n',2),('tool_choice','auto')]:
            with self.subTest(key=key):
                payload=copy.deepcopy(self.payload);payload[key]=value
                with self.assertRaises(ValueError): validate_payload(payload,self.model,self.messages)

    def test_oversize_request_rejected(self):
        messages=[{'role':'user','content':'x'*64_001}]
        payload=copy.deepcopy(self.payload);payload['messages']=messages
        with self.assertRaises(ValueError):validate_payload(payload,self.model,messages)

    def test_five_attempt_cap_and_pending_counts(self):
        ledger=self.ledger()
        for _ in range(5): ledger.reserve(self.model,'digest')
        with self.assertRaises(BudgetStop):ledger.reserve(self.model,'digest')
        self.assertEqual(len(json.loads(ledger.path.read_text())['attempts']),5)

    def test_total_cap_25(self):
        ledger=self.ledger()
        for model in MODELS:
            for _ in range(5):ledger.reserve(model,'digest')
        with self.assertRaises(BudgetStop):ledger.reserve(MODELS[-1],'digest')

    def test_quota_halt_blocks_all_models_and_persists(self):
        ledger=Ledger(self.path/'ledger.json');ledger.halt_quota('53870');ledger.close()
        ledger=self.ledger()
        for model in MODELS:
            with self.assertRaisesRegex(BudgetStop,'free_quota'):ledger.reserve(model,'digest')
        self.assertEqual(ledger.state['attempts'],[])

    def test_reopen_pending_halts_model(self):
        ledger=Ledger(self.path/'ledger.json');ledger.reserve(self.model,'digest');ledger.close()
        ledger=self.ledger()
        with self.assertRaisesRegex(BudgetStop,'unresolved'):ledger.check(self.model)

    def test_account_credentials_are_not_inherited(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':'private','OPENCODE_API_KEY':'private','HOME':'private'}):
            env=isolated_env(self.path,config_for(self.model,self.messages,12345))
        self.assertNotIn('HOME',env);self.assertNotIn('OPENCODE_API_KEY',env);self.assertNotIn('OPENAI_API_KEY',env)
        self.assertNotIn('private',json.dumps(env))

    def test_maintenance_agents_disabled_and_exact_body(self):
        config=config_for(self.model,self.messages,12345)
        for agent in ['title','summary','compaction','explore','general']:self.assertTrue(config['agents'][agent]['disabled'])
        self.assertFalse(config['warming']);self.assertFalse(config['compaction']['auto'])
        body=config['providers']['opencode']['body']
        self.assertEqual(body['messages'],self.messages);self.assertEqual(body['tools'],[])

    def test_confirmed_free_sse_only(self):
        raw=fake_response(self.model)
        text,usage=parse_stream(raw,self.model);self.assertEqual(json.loads(text)['tool'],'inspect')
        for modified in [raw.replace(b'"cost": 0',b'"cost": 1'),
                         raw.replace(b'"billing_source": "free"',b'"billing_source": "balance"'),
                         raw.replace(b'"finish_reason": "stop"',b'"finish_reason": "length"')]:
            with self.assertRaises(ValueError):parse_stream(modified,self.model)

    def test_profile_allows_only_own_state_and_two_ports(self):
        text=sandbox_profile(self.path,12345,23456)
        self.assertIn('localhost:12345',text);self.assertIn('localhost:23456',text)
        self.assertNotIn('localhost:*',text)
        self.assertIn('(subpath "/Users")',text)
        self.assertIn('(deny file-write* (require-not',text)


if __name__=='__main__':unittest.main()
