"""Stateless HTTPS chat-completions wire contract, with no retries or redirects."""
import json
import os
import uuid
import urllib.request
import urllib.error
from .budget import BudgetStop


class ProviderStop(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderStop('redirect_refused')


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON number')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)


def contains_secret(value, secret):
    if isinstance(value, str):
        return secret in value
    if isinstance(value, dict):
        return any(contains_secret(k, secret) or contains_secret(v, secret) for k, v in value.items())
    if isinstance(value, list):
        return any(contains_secret(v, secret) for v in value)
    return False


class HTTPTransport:
    def __init__(self, config, *, live=False):
        if not live or not config.live_enabled:
            raise ProviderStop('live_calls_not_enabled')
        self.config = config
        self._key = os.environ.get(config.api_key_env, '')
        if not self._key or '\n' in self._key or '\r' in self._key:
            raise ProviderStop('missing_or_invalid_api_key')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def send(self, payload, request_id):
        c = self.config
        req = urllib.request.Request(c.endpoint, data=json.dumps(payload, separators=(',', ':'), allow_nan=False).encode(),
                headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._key,
                         'X-Client-Request-Id': request_id}, method='POST')
        try:
            with self.opener.open(req, timeout=c.timeout_seconds) as response:
                data = response.read(c.max_response_bytes + 1)
                if len(data) > c.max_response_bytes:
                    raise ProviderStop('response_too_large')
                decoded = data.decode('utf-8')
                # A provider must never reflect a bearer credential into saved artifacts.
                parsed = strict_json(decoded)
                if self._key in decoded or contains_secret(parsed, self._key):
                    raise ProviderStop('credential_echo_refused')
                return parsed
        except urllib.error.HTTPError as error:
            # Do not read/log an error body or URL that may contain credentials.
            raise ProviderStop('http_' + str(error.code)) from None
        except ProviderStop:
            raise
        except Exception:
            raise ProviderStop('transport_failure') from None


class Client:
    def __init__(self, config, ledger, transport, log):
        if config != ledger.config or (isinstance(transport, HTTPTransport) and config != transport.config):
            raise ValueError('client, ledger and transport must use the same provider contract')
        self.config, self.ledger, self.transport, self.log = config, ledger, transport, log

    def payload(self, messages):
        # JSON mode is deliberately the minimal wire contract. Typed tool schemas
        # remain in the public prompt and are independently enforced before dispatch.
        return {'model': self.config.model, 'messages': messages, 'n': 1, 'stream': False,
                'store': False, self.config.output_limit_field: self.config.output_tokens_per_call,
                'response_format': {'type': 'json_object'}}

    def complete(self, messages):
        payload = self.payload(messages)
        request_id = uuid.uuid4().hex  # fresh identifier, never a continuation ID
        self.ledger.reserve(request_id)
        try:
            self.log({'kind': 'request', 'request_id': request_id, 'payload': payload})
            response = self.transport.send(payload, request_id)
        except Exception as error:
            allowed = {'redirect_refused', 'response_too_large', 'credential_echo_refused', 'transport_failure'}
            code = str(error) if isinstance(error, ProviderStop) else ''
            if code not in allowed and not (len(code) == 8 and code.startswith('http_') and code[5:].isdigit()):
                code = 'transport_or_request_log_failure'
            self.ledger.uncertain(code)
            # Do not copy arbitrary exception text (provider errors can echo keys).
            raise ProviderStop('request_failed_charge_unknown') from None
        try:
            self.log({'kind': 'response', 'request_id': request_id, 'response': response})
        except Exception:
            self.ledger.uncertain('response_log_failure')
            raise ProviderStop('response_log_failure') from None
        usage = response.get('usage') if type(response) is dict else None
        self.ledger.settle(request_id, usage)
        try:
            choices = response.get('choices')
            if type(choices) is not list or len(choices) != 1 or type(choices[0]) is not dict:
                raise ValueError('choices')
            choice = choices[0]
            message = choice.get('message')
            if (choice.get('finish_reason') != 'stop' or type(message) is not dict or message.get('refusal')
                    or message.get('tool_calls') or message.get('function_call') or type(message.get('content')) is not str):
                raise ValueError('unfinished/refused/non-text response')
            return message['content']
        except Exception:
            self.ledger.halt('invalid_provider_response')
            raise ProviderStop('invalid_provider_response') from None
