"""Explicit provider contract and limits; no guessed live prices or token counts."""
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def local_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('path must stay inside Lexi')
    return path


def positive_int(value, name):
    if type(value) is not int or value <= 0 or value > 1000000000:
        raise ValueError(name + ' must be an integer between1 and1000000000')
    return value


def money(value, name):
    if type(value) is not str:
        raise ValueError(name + ' must be an exact decimal string')
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError(name + ' must be decimal') from None
    if not result.is_finite() or result <= 0 or result.as_tuple().exponent < -12 or result > Decimal('1000000'):
        raise ValueError(name + ' must be finite, positive, and have at most12 decimal places')
    return result


@dataclass(frozen=True)
class Config:
    endpoint: str
    model: str
    api_key_env: str
    # Must be the provider-enforced FULL context window, not a desired prompt size.
    context_window: int
    input_usd_per_million: str
    output_usd_per_million: str
    budget_usd: str
    max_calls: int
    max_input_tokens: int
    max_output_tokens: int
    output_tokens_per_call: int
    pricing_note: str
    live_enabled: bool = False
    output_limit_field: str = 'max_tokens'
    timeout_seconds: int = 30
    max_response_bytes: int = 2097152
    no_progress_limit: int = 3

    def __post_init__(self):
        if type(self.endpoint) is not str:
            raise ValueError('endpoint must be a string')
        url = urlsplit(self.endpoint)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment
                or not url.path.endswith('/chat/completions') or any(ord(c) <= 32 for c in self.endpoint)):
            raise ValueError('use a clean HTTPS chat/completions URL without credentials, query or fragment')
        for name in ('model', 'pricing_note'):
            if type(getattr(self, name)) is not str or not getattr(self, name).strip():
                raise ValueError(name + ' is required')
        if type(self.api_key_env) is not str or not re.fullmatch(r'[A-Z][A-Z0-9_]*', self.api_key_env):
            raise ValueError('api_key_env must name one explicit environment variable')
        for name in ('context_window', 'max_calls', 'max_input_tokens', 'max_output_tokens',
                     'output_tokens_per_call', 'timeout_seconds', 'max_response_bytes', 'no_progress_limit'):
            positive_int(getattr(self, name), name)
        if self.timeout_seconds > 60 or self.output_tokens_per_call > self.context_window:
            raise ValueError('timeout must be <=60; output limit must fit context')
        if type(self.live_enabled) is not bool:
            raise ValueError('live_enabled must be Boolean')
        if self.output_limit_field not in ('max_tokens', 'max_completion_tokens'):
            raise ValueError('unsupported output limit field')
        for name in ('input_usd_per_million', 'output_usd_per_million', 'budget_usd'):
            money(getattr(self, name), name)

    def cost(self, inputs, outputs):
        return (Decimal(inputs) * money(self.input_usd_per_million, 'input price') +
                Decimal(outputs) * money(self.output_usd_per_million, 'output price')) / Decimal(1000000)

    @property
    def reservation(self):
        # No tokenizer approximation, cached-token discount or billing refund is assumed.
        return self.cost(self.context_window, self.output_tokens_per_call)

    def contract(self):
        return asdict(self)

    @classmethod
    def read(cls, path):
        return cls(**json.loads(local_path(path).read_text()))
