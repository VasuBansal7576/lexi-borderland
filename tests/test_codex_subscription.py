import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from baseline.codex_subscription.bridge import (BASE,MODEL,CAP,Ledger,public_payload,normalize,parse_sse,
                                               fake_sse,auth_state,ProviderStop,BudgetStop,UPSTREAM_HOST,UPSTREAM_PATH)
from baseline.codex_subscription.native import environment,profile

class NativeSubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=BASE);self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)
        self.messages=[{'role':'system','content':'public rules'},{'role':'user','content':'public observation'}]
        self.raw={'model':MODEL,'input':[{'role':'developer','content':[{'type':'input_text','text':'public rules'}]},
            {'type':'additional_tools','tools':[{'name':'read_all_files'}]},
            {'role':'developer','content':[{'type':'input_text','text':'ambient coding instructions'}]},
            {'role':'user','content':[{'type':'input_text','text':'public observation'}]}]}
    def ledger(self):
        x=Ledger(self.path/'ledger.json');self.addCleanup(x.close);return x
    def test_exact_public_messages_and_no_tools(self):
        body=normalize(self.raw,self.messages)
        self.assertEqual(body,public_payload(self.messages));self.assertEqual(body['tools'],[])
        self.assertNotIn('ambient',json.dumps(body));self.assertNotIn('read_all_files',json.dumps(body))
        self.assertEqual(body['max_output_tokens'],CAP);self.assertFalse(body['store'])
    def test_substitution_changed_prompt_and_provider_history_rejected(self):
        for change in [{'model':'gpt-6-astra'},{'previous_response_id':'prior'},{'conversation':'prior'},{'input':[]}]:
            with self.assertRaises(ValueError):normalize({**self.raw,**change},self.messages)
    def test_input_limit(self):
        value=copy.deepcopy(self.messages);value[1]['content']='x'*64001
        with self.assertRaises(ValueError):public_payload(value)
    def test_durable_five_attempt_cap(self):
        ledger=self.ledger()
        for _ in range(5):ledger.reserve(b'public')
        with self.assertRaises(BudgetStop):ledger.reserve(b'public')
        self.assertEqual(len(json.loads(ledger.path.read_text())['attempts']),5)
    def test_reopen_pending_blocks(self):
        x=Ledger(self.path/'ledger.json');x.reserve(b'public');x.close()
        x=self.ledger()
        with self.assertRaisesRegex(BudgetStop,'unresolved'):x.check()
    def test_hundred_attempt_budget_persists_and_blocks_101(self):
        x=Ledger(self.path/'hundred.json',max_calls=100)
        for _ in range(100):
            n=x.reserve(b'public');x.finish(n,status='complete')
        x.close()
        x=Ledger(self.path/'hundred.json',max_calls=100);self.addCleanup(x.close)
        self.assertEqual(len(x.state['attempts']),100)
        with self.assertRaisesRegex(BudgetStop,'model_call_limit'):x.reserve(b'public')
    def test_existing_budget_cannot_be_raised(self):
        x=Ledger(self.path/'ledger.json');x.close()
        with self.assertRaisesRegex(ValueError,'contract_mismatch'):Ledger(self.path/'ledger.json',max_calls=100)
    def test_call_limit_rejects_unbounded_and_noninteger_values(self):
        for value in [0,101,-1,True,1.5,'100']:
            with self.assertRaises(ValueError):Ledger(self.path/'ledger.json',max_calls=value)
    def test_halt_no_fallback(self):
        x=self.ledger();x.halt('subscription_http_429')
        with self.assertRaisesRegex(BudgetStop,'429'):x.reserve(b'public')
    def test_api_credentials_rejected(self):
        (self.path/'state').mkdir()
        for obj in [{'auth_mode':'apikey','OPENAI_API_KEY':'fake-test-key'},
                    {'auth_mode':'chatgpt','OPENAI_API_KEY':'fake-test-key'},
                    {'auth_mode':'chatgpt','tokens':{}}]:
            (self.path/'state/auth.json').write_text(json.dumps(obj))
            with patch('baseline.codex_subscription.bridge.AUTH_STATE',self.path):
                with self.assertRaises(ProviderStop):auth_state(live=True)
    def test_minimal_environment_and_native_client_only(self):
        env=environment(self.path)
        self.assertNotIn('OPENAI_API_KEY',env);self.assertNotIn('CODEX_API_KEY',env);self.assertNotIn('HOME',env)
        self.assertEqual(env['CODEX_HOME'],str(self.path/'state'))
        self.assertNotIn('opencode',profile(self.path,relay_port=12345))
        self.assertEqual(UPSTREAM_HOST,'chatgpt.com');self.assertEqual(UPSTREAM_PATH,'/backend-api/codex/responses')
    def test_sse_requires_completed_output_with_usage(self):
        text,usage=parse_sse(fake_sse());self.assertEqual(json.loads(text)['tool'],'inspect')
        for raw in [fake_sse().replace(b'"output_tokens": 20',b'"output_tokens": 9999'),
                    fake_sse().replace(b'"response.completed"',b'"response.incomplete"'),
                    fake_sse().replace(b'"model": "gpt-6.1-terra"',b'"model": "gpt-6-astra"')]:
            with self.assertRaises(ValueError):parse_sse(raw)

if __name__=='__main__':unittest.main()
