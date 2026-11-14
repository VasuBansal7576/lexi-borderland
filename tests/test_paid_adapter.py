"""All provider calls are fakes; outbound socket operations are forbidden."""
import copy
from dataclasses import replace
from decimal import Decimal
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch, Mock
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import urllib.error
import urllib.request

from baseline.paid.config import Config, ROOT, local_path
from baseline.paid.budget import Ledger, BudgetStop
from baseline.paid.client import Client, HTTPTransport, ProviderStop, NoRedirect, strict_json
from baseline.paid.run import PaidHistory, run_episode, EventLog, main
from baseline.paid.guard import LoopGuard
from baseline.interface_v3 import response_schema
from borderland.env import BorderlandEnv

SOURCE = ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'


def response(action=None, *, inputs=100, outputs=20, finish='stop'):
    action = action or {'reason': 'fake', 'tool': 'status', 'args': {}}
    return {'choices': [{'finish_reason': finish, 'message': {'content': json.dumps(action)}}],
            'usage': {'prompt_tokens': inputs, 'completion_tokens': outputs, 'total_tokens': inputs+outputs}}


class FakeTransport:
    def __init__(self, values):
        self.values = iter(values)
        self.requests = []

    def send(self, payload, request_id):
        self.requests.append(copy.deepcopy(payload))
        value = next(self.values)
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)


class PaidAdapterTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'runtime/test-tmp').mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'runtime/test-tmp')
        self.path = Path(self.tmp.name)
        self.c = Config.read('baseline/paid/offline-example.json')
        self.ledgers = []
        self.network = []
        for name in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.socket.sendto', 'socket.create_connection', 'socket.getaddrinfo'):
            mock = self.enterContext(patch(name, side_effect=AssertionError('NETWORK FORBIDDEN IN OFFLINE TEST')))
            self.network.append(mock)

    # unittest.enterContext is not available in the project's Python3.9.
    def enterContext(self, context):
        result = context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
        return result

    def tearDown(self):
        for ledger in self.ledgers:
            ledger.close()
        self.tmp.cleanup()
        for mocked in self.network:
            self.assertEqual(mocked.call_count, 0, 'an outbound network operation was attempted')

    def ledger(self, config=None, name='ledger.json'):
        ledger = Ledger(config or self.c, self.path/name)
        self.ledgers.append(ledger)
        return ledger

    def client(self, values, config=None, name='ledger.json'):
        ledger = self.ledger(config, name)
        transport = FakeTransport(values)
        events = []
        return Client(config or self.c, ledger, transport, events.append), transport, events

    def run_fake(self, values, config=None, world=None):
        config = config or self.c
        folder = self.path/'run'; folder.mkdir()
        log = EventLog(folder/'events.jsonl'); self.addCleanup(log.close)
        ledger = self.ledger(config)
        fake = FakeTransport(values)
        client = Client(config, ledger, fake, log)
        env = BorderlandEnv(world=world or json.loads((SOURCE/'manifest.json').read_text()))
        report = run_episode(env, client, folder, mode='offline_test_fixture_not_model')
        return report, fake, env

    def test_config_rejects_unsafe_urls_bad_limits_unknown_fields_and_floats(self):
        for change in ({'endpoint': 'http://api.invalid/chat/completions'},
                       {'endpoint': 'https://key@api.invalid/chat/completions'},
                       {'endpoint': 'https://api.invalid/chat/completions?key=secret'},
                       {'budget_usd': 'NaN'}, {'budget_usd': '-1'}, {'budget_usd': .1},
                       {'max_calls': True}, {'max_calls': 0}, {'live_enabled': 'false'},
                       {'timeout_seconds': 61}, {'output_limit_field': 'unbounded'},
                       {'api_key_env': 'bad\nheader'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(self.c, **change)
        with self.assertRaises(TypeError):
            Config(**dict(self.c.contract(), unexpected=True))
        with self.assertRaises(ValueError):
            local_path('/outside-lexi/not-read')

    def test_reservation_exact_decimal_and_written_before_transport(self):
        self.assertEqual(self.c.reservation, Decimal('0.016256'))
        client, fake, events = self.client([response()])
        original = fake.send
        def send(payload, request_id):
            state = json.loads(client.ledger.path.read_text())
            self.assertEqual(state['pending'], request_id)
            self.assertEqual(Decimal(state['cost_accounted_usd']), self.c.reservation)
            return original(payload, request_id)
        fake.send = send
        client.complete([{'role': 'user', 'content': 'synthetic'}])
        self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']), Decimal('0.00014'))
        self.assertEqual(client.ledger.state['input_tokens_accounted'], 100)
        self.assertIsNone(client.ledger.state['pending'])

    def test_every_budget_blocks_before_network(self):
        for number, change in enumerate(({'budget_usd': '0.016255999'}, {'max_input_tokens': 15999}, {'max_output_tokens': 127})):
            c = replace(self.c, **change)
            client, fake, _ = self.client([response()], c, str(number)+'.json')
            with self.assertRaises(BudgetStop):client.complete([])
            self.assertEqual(fake.requests, [])
            self.assertEqual(client.ledger.state['calls'], 0)
        c = replace(self.c, max_calls=1)
        client, fake, _ = self.client([response(), response()], c, 'calls.json')
        client.complete([])
        with self.assertRaisesRegex(BudgetStop, 'call_budget'):client.complete([])
        self.assertEqual(len(fake.requests), 1)

    def test_exact_dollar_boundary_allows_one_reservation_then_blocks(self):
        c = replace(self.c, budget_usd=str(self.c.reservation))
        client, fake, _ = self.client([response(inputs=16000, outputs=128), response()], c)
        client.complete([])
        with self.assertRaisesRegex(BudgetStop, 'dollar_budget'):client.complete([])
        self.assertEqual(len(fake.requests), 1)
        self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']), Decimal(c.budget_usd))

    def test_token_budgets_are_cumulative_even_after_settlement(self):
        for name, changes, expected in [('input', {'max_input_tokens': 16099}, 'input_token_budget'),
                                        ('output', {'max_output_tokens': 147}, 'output_token_budget')]:
            c = replace(self.c, **changes)
            client, fake, _ = self.client([response(), response()], c, name+'.json')
            client.complete([])
            with self.assertRaisesRegex(BudgetStop, expected):client.complete([])
            self.assertEqual(len(fake.requests), 1)

    def test_timeout_no_retry_no_refund_no_resume(self):
        client, fake, events = self.client([TimeoutError('secret-must-not-be-logged'), response()])
        with self.assertRaises(ProviderStop):client.complete([])
        self.assertEqual(len(fake.requests), 1)
        self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']), self.c.reservation)
        self.assertNotIn('secret-must-not-be-logged', json.dumps(client.ledger.state)+json.dumps(events))
        with self.assertRaises(BudgetStop):client.complete([])
        client.ledger.close()
        with self.assertRaisesRegex(BudgetStop, 'unresolved_charge'):self.ledger()
        self.assertEqual(len(fake.requests), 1)

    def test_pending_reservation_survives_crash(self):
        ledger = self.ledger(); ledger.reserve('before-crash'); ledger.close()
        with self.assertRaisesRegex(BudgetStop, 'unresolved_charge'):self.ledger()
        state = json.loads((self.path/'ledger.json').read_text())
        self.assertEqual(state['calls'], 1)
        self.assertEqual(state['pending'], 'before-crash')

    def test_ledger_reopen_preserves_spend_and_rejects_config_reset(self):
        c = replace(self.c, max_calls=1)
        client, fake, _ = self.client([response()], c)
        client.complete([]); client.ledger.close()
        reopened = self.ledger(c)
        with self.assertRaisesRegex(BudgetStop, 'call_budget'):reopened.reserve('second')
        reopened.close()
        with self.assertRaisesRegex(BudgetStop, 'config_mismatch'):self.ledger(replace(c, max_calls=2))

    def test_ledger_lock_prevents_concurrent_runners(self):
        self.ledger()
        with self.assertRaisesRegex(BudgetStop, 'ledger_in_use'):self.ledger()

    def test_threaded_reservations_cannot_double_spend(self):
        ledger = self.ledger(); barrier = Barrier(2)
        def reserve(i):
            barrier.wait()
            try: ledger.reserve(str(i)); return 'reserved'
            except BudgetStop:return 'blocked'
        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(reserve, (1,2)))
        self.assertEqual(sorted(result), ['blocked', 'reserved'])
        self.assertEqual(ledger.state['calls'], 1)

    def test_invalid_missing_and_over_limit_usage_halt(self):
        cases = [None, {}, {'prompt_tokens': True, 'completion_tokens': 2, 'total_tokens': 3},
                 {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 0},
                 {'prompt_tokens': 16001, 'completion_tokens': 1, 'total_tokens': 16002},
                 {'prompt_tokens': 1, 'completion_tokens': 129, 'total_tokens': 130}]
        for i, usage in enumerate(cases):
            r = response(); r['usage'] = usage
            client, fake, _ = self.client([r, response()], name=str(i)+'.json')
            with self.assertRaises(BudgetStop):client.complete([])
            with self.assertRaises(BudgetStop):client.complete([])
            self.assertEqual(len(fake.requests), 1)
            self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']), self.c.reservation)

    def test_refusal_truncation_and_extra_choices_charge_once_then_stop(self):
        refusal = response(); refusal['choices'][0]['message']['refusal'] = 'no'
        extra = response(); extra['choices'].append(copy.deepcopy(extra['choices'][0]))
        tools = response(); tools['choices'][0]['message']['tool_calls'] = [{'bad': 'shape'}]
        for i, r in enumerate((response(finish='length'), refusal, extra, tools)):
            client, fake, _ = self.client([r, response()], name=str(i)+'.json')
            with self.assertRaises(ProviderStop):client.complete([])
            with self.assertRaises(BudgetStop):client.complete([])
            self.assertEqual(len(fake.requests), 1)
            self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']), Decimal('0.00014'))

    def test_live_transport_needs_both_opt_ins_and_never_sends_by_constructing(self):
        with patch.dict('os.environ', {'LEXI_PAID_API_KEY': 'synthetic-secret'}):
            for c, live in ((self.c, True), (replace(self.c, live_enabled=True), False)):
                with self.assertRaises(ProviderStop):HTTPTransport(c, live=live)
            with patch('urllib.request.build_opener') as builder:
                HTTPTransport(replace(self.c, live_enabled=True), live=True)
                builder.return_value.open.assert_not_called()

    def test_https_wire_headers_limits_no_credentials_in_payload_or_logs(self):
        c = replace(self.c, live_enabled=True, output_limit_field='max_completion_tokens')
        remote = Mock(); remote.__enter__ = Mock(return_value=remote); remote.__exit__ = Mock(return_value=False)
        remote.read.return_value = json.dumps(response()).encode()
        opener = Mock(); opener.open.return_value = remote
        with patch.dict('os.environ', {'LEXI_PAID_API_KEY': 'synthetic-secret'}), patch('urllib.request.build_opener', return_value=opener):
            transport = HTTPTransport(c, live=True)
            logs=[]; client = Client(c, self.ledger(c), transport, logs.append)
            client.complete([{'role':'user','content':'public synthetic message'}])
        req = opener.open.call_args[0][0]
        self.assertEqual(req.get_header('Authorization'), 'Bearer synthetic-secret')
        body = json.loads(req.data)
        self.assertEqual(body['max_completion_tokens'], 128)
        self.assertNotIn('max_tokens', body)
        self.assertEqual(body['n'], 1); self.assertFalse(body['stream']); self.assertFalse(body['store'])
        self.assertEqual(body['response_format'], {'type':'json_object'})
        self.assertNotIn('synthetic-secret', json.dumps(logs)+json.dumps(client.ledger.state))
        remote.read.assert_called_once_with(c.max_response_bytes+1)

    def test_redirect_http_errors_and_credential_echo_never_retry_or_log_secrets(self):
        with self.assertRaisesRegex(ProviderStop, 'redirect_refused'):
            NoRedirect().redirect_request(None,None,302,'',{},'https://elsewhere.invalid')
        c = replace(self.c, live_enabled=True)
        for i, failure in enumerate((urllib.error.HTTPError(c.endpoint, 429, 'synthetic-secret', {}, None), TimeoutError())):
            opener=Mock(); opener.open.side_effect=failure
            with patch.dict('os.environ', {'LEXI_PAID_API_KEY':'synthetic-secret'}), patch('urllib.request.build_opener',return_value=opener):
                client=Client(c,self.ledger(c,str(i)+'.json'),HTTPTransport(c,live=True),lambda value:None)
                with self.assertRaises(ProviderStop):client.complete([])
            self.assertEqual(opener.open.call_count,1)
            self.assertNotIn('synthetic-secret',json.dumps(client.ledger.state))
        remote=Mock();remote.__enter__=Mock(return_value=remote);remote.__exit__=Mock(return_value=False)
        remote.read.return_value=b'{"echo":"synthetic-secret"}'
        opener=Mock();opener.open.return_value=remote
        with patch.dict('os.environ', {'LEXI_PAID_API_KEY':'synthetic-secret'}),patch('urllib.request.build_opener',return_value=opener):
            transport=HTTPTransport(c,live=True)
            with self.assertRaisesRegex(ProviderStop,'credential_echo_refused'):transport.send({},'fake')

    def test_strict_json_rejects_duplicate_keys_nonfinite_and_prose(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', 'here is your action'):
            with self.assertRaises(ValueError):strict_json(raw)

    def test_loop_guard_stops_rules_even_with_clock_and_reason_changes(self):
        actions=[response({'reason':str(i),'tool':'inspect','args':{'object_id':'rules'}}) for i in range(10)]
        report,fake,env=self.run_fake(actions)
        self.assertEqual(report['stop'],'evaluator_no_progress')
        self.assertEqual(len(fake.requests),4)
        self.assertFalse(env.terminated or env.truncated)
        self.assertIsNone(report['environment_reason'])
        self.assertTrue(report['external_stop'])
        self.assertEqual(len(env.trace),4)

    def test_alternating_passive_calls_and_changing_notebooks_do_not_evade_guard(self):
        guard=LoopGuard(3);env=BorderlandEnv(0)
        frame={'ok':True,'result':{},'observation':env.observe()}
        for i, tool in enumerate(('status','notebook_write','notebook_read')):
            action={'tool':tool,'args':{'lines':[str(i)]*8} if tool=='notebook_write' else {}}
            after=env.step(action).observation
            self.assertEqual(guard.observe(frame,action,after),i==2)
            frame=after

    def test_novel_pages_and_legitimate_timing_round_progress_do_not_trigger_guard(self):
        guard=LoopGuard(3)
        base={'ok':True,'result':{},'observation':{'room':1,'notebook':['']*8,'clock':0}}
        for offset in range(8):
            after=copy.deepcopy(base);after['result']={'text':str(offset),'evidence_id':'synthetic','next_offset':offset+1}
            self.assertFalse(guard.observe(base,{'tool':'read_record','args':{'offset':offset}},after))
        for room, field, tool in ((4,'clock','wait'),(7,'round','team_step')):
            before={'ok':True,'result':{},'observation':{'room':room,'notebook':['']*8,field:0}}
            for tick in range(1,9):
                after=copy.deepcopy(before);after['observation'][field]=tick
                self.assertFalse(guard.observe(before,{'tool':tool,'args':{}},after));before=after

    def test_malformed_action_is_not_repaired_or_dispatched(self):
        report,fake,env=self.run_fake([response({'reason':'bad','tool':'inspect','args':{'wrong':'rules'}}),response()])
        self.assertEqual(report['stop'],'invalid_model_action')
        self.assertEqual(len(fake.requests),1);self.assertEqual(env.trace,[])

    def test_unsafe_valid_action_still_fails_in_unchanged_engine(self):
        report,fake,env=self.run_fake([response({'reason':'synthetic unsafe test','tool':'choose_door','args':{'door_id':'C'}})])
        self.assertTrue(env.terminated);self.assertEqual(env.reason,'unsafe_door')
        self.assertFalse(report['external_stop']);self.assertFalse(report['success'])

    def test_all_seven_rooms_fake_fixture_and_actual_wipe_payload(self):
        # Evaluator-only scripted responses: not an LLM solve or leaked prompt.
        witness=[json.loads(x) for x in (SOURCE/'trace.jsonl').read_text().splitlines()]
        values=[response({'reason':'offline fixture response',**row['action']}) for row in witness]
        c=replace(self.c,max_calls=160,max_input_tokens=3000000,max_output_tokens=30000,budget_usd='10')
        report,fake,env=self.run_fake(values,c)
        self.assertTrue(report['success']);self.assertEqual(env.room,7)
        self.assertEqual(len(fake.requests),len(witness));self.assertEqual(len(report['wipes']),1)
        wipe=report['wipes'][0];index=wipe['after_action']+1
        payload=fake.requests[index];content=json.loads(payload['messages'][1]['content'])
        packed=content['history_since_last_wipe']
        self.assertEqual(len(packed['events']),1)
        self.assertNotIn('previous_model_output',packed['events'][0]['event'])
        self.assertEqual(packed['results'],[{'ok':True,'result':{}}])
        self.assertEqual(content['current_state']['notebook'],wipe['notebook'])
        self.assertEqual(len(wipe['notebook']),8)
        self.assertTrue(all(len(line)<=96 for line in wipe['notebook']))
        for request in fake.requests:
            self.assertEqual(set(request),{'model','messages','n','stream','store','max_tokens','response_format'})
        self.assertEqual(report['ledger']['calls'],len(witness))  # accounting did not reset at wipe
        self.assertGreater(report['ledger']['input_tokens_accounted'],100*index)
        # Every request reconstructed from actual public frames and the model's preceding output.
        saved=json.loads((self.path/'run/actions.json').read_text());history=PaidHistory()
        for i,row in enumerate(saved):
            history.add(row['public_frame'])
            self.assertEqual(fake.requests[i]['messages'],history.messages())
            history.act(json.loads(row['raw']))
            if i==wipe['after_action']:history=PaidHistory()

    def test_paid_wipe_blank_notebook_prompts_identical_across_hidden_twins(self):
        prompts=[]
        for phase,sigma in ((0,0),(0,1),(1,0),(1,1)):
            source=SOURCE.parent/f'phase-{phase}-sigma-{sigma}'
            env=BorderlandEnv(world=json.loads((source/'manifest.json').read_text()))
            for line in (source/'trace.jsonl').read_text().splitlines():
                action=json.loads(line)['action']
                if action['tool']=='notebook_write':action={'tool':'notebook_write','args':{'lines':['']*8}}
                result=env.step(action)
                if result.info['epoch_changed']:break
            history=PaidHistory();history.add({'ok':True,'result':{},'observation':env.observe()})
            prompts.append(history.messages())
            self.assertEqual(len(response_schema(env.observe())['anyOf']),len(env.tools()))
        self.assertTrue(all(p==prompts[0] for p in prompts))

    def test_default_cli_is_preflight_without_credentials_transport_or_ledger(self):
        args=['paid','--config','baseline/paid/offline-example.json']
        with patch('sys.argv',args),patch('baseline.paid.run.HTTPTransport') as http,patch('baseline.paid.run.Ledger') as ledger,patch('sys.stdout',new_callable=io.StringIO) as stdout:
            main()
        http.assert_not_called();ledger.assert_not_called()
        result=json.loads(stdout.getvalue())
        self.assertEqual(result['network_calls'],0)
        self.assertEqual(result['mode'],'offline_preflight')
        self.assertTrue(result['first_request_affordable'])

    def test_storage_failure_blocks_send_and_future_attempts(self):
        client,fake,_=self.client([response()])
        with patch('baseline.paid.budget.persist',side_effect=OSError('disk unavailable')):
            with self.assertRaisesRegex(BudgetStop,'ledger_storage_failure'):client.complete([])
        with self.assertRaisesRegex(BudgetStop,'ledger_storage_failure'):client.complete([])
        self.assertEqual(fake.requests,[])

    def test_corrupted_journal_fails_closed(self):
        client,_,_=self.client([response()]);client.complete([]);client.ledger.close()
        path=self.path/'ledger.json';state=json.loads(path.read_text())
        state['cost_accounted_usd']='0';path.write_text(json.dumps(state))
        with self.assertRaisesRegex(BudgetStop,'invalid_ledger'):self.ledger()

    def test_guard_stops_invalid_actions_despite_clock_changes(self):
        guard=LoopGuard(3)
        before={'ok':True,'result':{},'observation':{'room':4,'clock':0,'notebook':['']*8}}
        for tick in range(1,4):
            after={'ok':False,'result':{'error':'invalid'},'observation':{'room':4,'clock':tick,'notebook':['']*8}}
            self.assertEqual(guard.observe(before,{'tool':'move','args':{}},after),tick==3)
            before=after

    def test_oversized_response_and_log_failure_stop_without_retry(self):
        c=replace(self.c,live_enabled=True,max_response_bytes=10)
        remote=Mock();remote.__enter__=Mock(return_value=remote);remote.__exit__=Mock(return_value=False)
        remote.read.return_value=b'x'*11
        opener=Mock();opener.open.return_value=remote
        with patch.dict('os.environ',{'LEXI_PAID_API_KEY':'synthetic-secret'}),patch('urllib.request.build_opener',return_value=opener):
            transport=HTTPTransport(c,live=True)
            with self.assertRaisesRegex(ProviderStop,'response_too_large'):transport.send({},'fake')
        client,fake,_=self.client([response()])
        client.log=Mock(side_effect=OSError('log full'))
        with self.assertRaises(ProviderStop):client.complete([])
        self.assertEqual(fake.requests,[])
        self.assertEqual(Decimal(client.ledger.state['cost_accounted_usd']),self.c.reservation)

    def test_client_cannot_mix_pricing_contracts(self):
        ledger=self.ledger()
        with self.assertRaises(ValueError):
            Client(replace(self.c,model='different-contract'),ledger,FakeTransport([]),lambda event:None)

    def test_closed_ledger_cannot_send_after_releasing_its_lock(self):
        client,fake,_=self.client([response()]);client.ledger.close()
        with self.assertRaisesRegex(BudgetStop,'ledger_closed'):client.complete([])
        self.assertEqual(fake.requests,[])

    def test_escaped_credential_echo_is_rejected_after_json_decode(self):
        c=replace(self.c,live_enabled=True)
        remote=Mock();remote.__enter__=Mock(return_value=remote);remote.__exit__=Mock(return_value=False)
        encoded=''.join(chr(92)+'u'+format(ord(x),'04x') for x in 'synthetic-secret')
        remote.read.return_value=('{"echo":"'+encoded+'"}').encode()
        opener=Mock();opener.open.return_value=remote
        with patch.dict('os.environ',{'LEXI_PAID_API_KEY':'synthetic-secret'}),patch('urllib.request.build_opener',return_value=opener):
            transport=HTTPTransport(c,live=True)
            with self.assertRaisesRegex(ProviderStop,'credential_echo_refused'):transport.send({},'fake')

    def test_offline_cli_ignores_live_enabled_and_uses_no_http_transport(self):
        config_path=self.path/'enabled-config.json'
        config_path.write_text(json.dumps(replace(self.c,live_enabled=True).contract()))
        folder=self.path/'cli-run';ledger_path=self.path/'cli-ledger.json'
        args=['paid','--config',str(config_path),'--offline-demo','--output',str(folder),'--ledger',str(ledger_path)]
        with patch('sys.argv',args),patch('baseline.paid.run.HTTPTransport') as http,patch('sys.stdout',new_callable=io.StringIO) as stdout:
            main()
        http.assert_not_called()
        result=json.loads(stdout.getvalue())
        self.assertEqual(result['mode'],'offline_fake')
        self.assertEqual(result['actions'],4)
        self.assertEqual(result['stop'],'evaluator_no_progress')
        self.assertEqual(json.loads(ledger_path.read_text())['calls'],4)
