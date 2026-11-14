"""Serialize suites sharing the local inference port; never overlap servers."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=ROOT/'artifacts/model-interface-v3/natural/summary.json'
started=time.monotonic()
while not summary.exists():
    if time.monotonic()-started>2400:raise TimeoutError('natural suite did not finish')
    time.sleep(1)
assert len(json.loads(summary.read_text()))==4
run_env=dict(os.environ, PYTHONPYCACHEPREFIX=str(ROOT/'runtime/pycache'))
for script in ('selection_smoke.py','memory_v3.py'):
    subprocess.run([sys.executable,str(ROOT/'evaluations'/script)],cwd=ROOT,env=run_env,check=True)
