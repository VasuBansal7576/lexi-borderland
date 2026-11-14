"""Correct an unused room4 state label after natural runs finish, before probes."""
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=ROOT/'artifacts/model-interface-v3/natural/summary.json'
while not summary.exists():time.sleep(.2)
p=ROOT/'baseline/interface_v3.py'
old=p.read_text()
assert 'If sealed_entry is true' in old
archive=ROOT/'artifacts/model-interface-v3/source-before-entry-wording/baseline'
archive.mkdir(parents=True,exist_ok=False)
(archive/p.name).write_text(old)
p.write_text(old.replace('If sealed_entry is true','If position is sealed_entry and unlocked is false'))
(ROOT/'artifacts/model-interface-v3/entry-wording-corrected.txt').write_text('Room4 request now uses the actual public position/unlocked fields. Natural room1 prompts unchanged. Prior adapter archived.\n')
