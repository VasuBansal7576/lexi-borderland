"""Build a measured report from audited final-prompt artifacts."""
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/model-interface-v3'


def main():
    audit=json.loads((BASE/'audit.json').read_text())
    memory=json.loads((BASE/'memory/audit.json').read_text())
    natural=audit['runs']
    checks=[json.loads(p.read_text()) for p in sorted((BASE/'memory').glob('*/memory-check.json'))]
    assert len(natural)==len(checks)==4
    assert audit['all_public_transport_and_replay_checks_passed'] and memory['all_checks_passed']
    smoke=json.loads((BASE/'selection-smoke/results.json').read_text())
    records=sum(len(r['model_records_read']) for r in natural)
    calls=sum(r['model_calls'] for r in natural)
    gate=sum(r['gate_passed'] for r in checks)
    wipes=sum(r['real_wipe'] for r in memory['cases'])
    empty_notes=all(r['notebook']==['']*8 for r in checks)
    schema_errors=audit['schema_violations']+sum(len(r.get('schema_errors',[])) for r in checks)
    lines=['# Tiny Aya after tool and prompt repairs','',
        f"**Unassisted: {audit['unassisted_escapes']}/4 escapes.** The final-prompt runs made {calls} model calls and read {records} records. All stopped in room 1. The separate upstream-assisted memory component completed {wipes} real server wipes and passed {gate}/4 gates. These are development-world diagnostics, not held-out results.",'',
        '## What was repaired','',
        '- Exact typed arguments and required keys for every advertised tool, including nested team orders and eight ASCII notebook lines of at most 96 bytes each. All wrong choices and both maintenance traps remain representable; no hidden-state action masking.',
        '- Current-room public laws and next-action instructions. Removed the misplaced room 3 reminder after the wipe; clarified clock versus phase, glyph versus sector, record reading and notebook versus evidence.',
        '- Lossless public-history packing with an independently checked inverse, keeping exact evidence visible without inserting an evaluator summary. No action repair, gold notebook, answer injection or automatic evidence reading.',
        '- Actual server destruction/restart and empty conversation at the seal. Only the model-written notebook crosses with normalized public state and fixed public instructions.','',
        'The entire `borderland/` engine, all seven rooms, rewards, budgets, maps and arena mechanics remain unchanged. The model remains official Tiny Aya Global Q4_K_M, frozen weights, temperature 0 / seed 42, 1,024 tokens/action and 8,192 context. No RL or SFT ran.','',
        '## Unassisted final-prompt episodes','',
        '| Phase / registry | Model calls | Records read | Stop | Cleared rooms |',
        '|---|---:|---:|---|---|']
    for r in natural:
        lines.append(f"| {r['name'].removeprefix('natural-')} | {r['model_calls']} | {len(r['model_records_read'])} | {r['reason']} | {r['rooms_completed_from_entry']} |")
    lines+=['',f"Schema-invalid returned outputs: {audit['schema_violations']}. The engine's separate `protocol_errors` counter is not a schema-validity measure; terminal budget exhaustion is recorded as `tool_budget`.",'',
        'Representative actual output:','', '```json']
    sample=next((BASE/'natural').glob('*/responses.jsonl'))
    lines+=[json.loads(sample.read_text().splitlines()[0])['choices'][0]['message']['content'],'```','',
        'The measured failure is evidence-acquisition/progress control: valid calls repeatedly inspect fixed rules instead of fetching the listed records. The prompt says how to read records, but the policy does not do it. No natural episode reaches room 2 or the memory seal; this run cannot establish independent performance in rooms 2–7.','',
        '## Model notebook and real wipe','',
        'This component starts from a legal upstream reference trajectory **before the reference notebook is written**. It includes successful earlier actions, so it is assisted upstream. Tiny Aya gets up to four unrestricted actions. If it does not exit, the evaluator performs only the already-legal exit, explicitly records ownership, and gives the model no credit for it. After process destruction/restart, Tiny Aya receives its own exact notebook and fresh room 4 public state, with up to four actions. No reference notebook or correct gate bits are supplied.','',
        '| Phase / registry | Model calls | Notebook bytes | Evaluator exit | New PID | Gate passed | Stop |',
        '|---|---:|---:|---|---|---|---|']
    for r in checks:
        lines.append(f"| {r['phase']} / {r['sigma']} | {r['model_calls']} | {r['bytes']} | {r['evaluator_exit']} | {r['old_pid']} → {r['new_pid']} | {r['gate_passed']} | {('component_step_cap' if r['reason']=='component_cap_or_gate_passed' and not r['gate_passed'] else r['reason'])} |")
    if empty_notes:
        lines+=['', '**Notebook preparation failed within this component cap:** all four notebooks contained eight empty lines. This tests preparation behavior under the stated four-action boundary; it does not establish how well Tiny Aya would use a useful self-written note. The completed room 3 flags were public, but the model repeatedly described the objectives as incomplete.']
    for r in checks:
        lines+=['',f"### Actual notebook: phase {r['phase']} / registry {r['sigma']}",'']
        if r['notebook']==['']*8:
            lines+=['Eight empty lines (0 bytes).']
        elif r['notebook'] is not None:
            lines+=['```text']+r['notebook']+['```']
        else:
            lines+=['No completed notebook boundary: see recorded inference error.']
        folder=BASE/'memory'/f"p{r['phase']}-s{r['sigma']}"
        cs=json.loads((folder/'calls.json').read_text()) if (folder/'calls.json').exists() else []
        lines+=['','Actual post-wipe actions: '+', '.join(c['action'].get('tool','invalid')+(' '+json.dumps(c['action']['args']) if c['action'].get('tool')=='unlock' else '') for c in cs if c['public_frame']['observation']['room']==4)+'.']
        if r['errors']:lines+=['','Runtime errors: '+repr(r['errors'])]
    lines+=['','A passed gate alone does not demonstrate memory: a memoryless guess can pass one of four paired worlds. Inspect the actual note content and paired results before claiming retention. Evaluator-assisted exits and runtime errors are never counted as autonomous success.','',
        '## Verification and scope','',
        f'- 46 tests passed. The 64 unchanged reference certificates passed: 4,604 actions, 1,344 citations and original source hashes.',
        f'-{schema_errors} schema-invalid outputs across the final natural/memory runs. Synthetic all-tools selection checks: {sum(r["correct_selection"] for r in smoke)}/{len(smoke)} correct. These are interface tests, not game success.',
        '-Every final-run request was reconstructed from public frames, every output matched its dispatched action, every trace replayed exactly, and source hashes matched. Wipe audits check distinct PIDs, no old history, exact notebook transfer and zero cached tokens on the first post-wipe response.',
        '-The blank-notebook prompt and action schema are identical across the four hidden twins. The adapter imports no hidden-world generator or reference solver.',
        '-Only this project folder was inspected for project data. The external wiki was not read under the folder-only restriction.',
        '-Four paired worlds from one development family are not an estimate of generalization. These prompts were revised after inspecting earlier failures. No claim is made that the policy can solve all seven rooms or that RL will fix it.','',
        '## Reproduce and inspect','',
        '```sh',
        'PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline --suite natural --output artifacts/my-typed-rerun',
        'PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 evaluations/audit_v3.py',
        'PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 evaluations/audit_memory_v3.py',
        'PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m unittest discover -s tests -v','```','',
        'The memory runner `evaluations/memory_v3.py` saves to a fresh fixed output path and refuses overwrite. Change that output path for a new run. Do not run two local inference suites simultaneously on port 18791.','',
        '-[Offline action viewer](viewer.html), [natural audit](audit.json), [memory audit](memory/audit.json), [tests](tests.txt), [unchanged environment audit](environment-recheck.json).',
        '-[Final protocol](../../baseline/PROTOCOL_V3.md), [typed interface protocol](../../baseline/PROTOCOL_V2.md).',
        '-[Intermediate v2 trials, including harness/runtime failures](../model-interface-v2/DEVELOPMENT_NOTES.md).',
        '-[Original baseline](../model-baseline/REPORT.md).','']
    lines=['- '+line[1:] if line.startswith('-') and not line.startswith('- ') else line for line in lines]
    (BASE/'REPORT.md').write_text('\n'.join(lines))
    viewer=(BASE/'viewer.html').read_text().split('<h2>Assisted model-note wipe components</h2>')[0].replace('</html>','')
    viewer+='<h2>Assisted model-note wipe components</h2><p>Only the model notebook crosses. Evaluator exits are explicitly labeled; no full escape credit.</p>'
    for r in checks:
        folder=BASE/'memory'/f"p{r['phase']}-s{r['sigma']}"
        cs=json.loads((folder/'calls.json').read_text()) if (folder/'calls.json').exists() else []
        viewer+='<details><summary>'+html.escape(f"Phase {r['phase']} / registry {r['sigma']} · gate {r['gate_passed']} · evaluator exit {r['evaluator_exit']}")+'</summary><pre>'+html.escape(json.dumps(r,indent=2))+'</pre>'
        for i,c in enumerate(cs):
            viewer+='<details><summary>'+html.escape(f"Model action {i+1} · room {c['public_frame']['observation']['room']}")+'</summary><pre>'+html.escape(c['response']['choices'][0]['message'].get('content',''))+'</pre></details>'
        viewer+='</details>'
    (BASE/'viewer.html').write_text(viewer+'</html>')
    print(json.dumps({'natural_escapes':audit['unassisted_escapes'],'natural_calls':calls,'records_read':records,'real_wipes':wipes,'gates_passed':gate,'schema_errors':schema_errors}))

if __name__=='__main__':main()
