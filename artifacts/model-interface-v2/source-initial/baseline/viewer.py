"""Make an offline viewer of actual model actions, never a synthetic demo."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/model-baseline"


def main():
    runs = []
    for report_path in sorted(BASE.glob("*-v1/*/report.json")):
        report = json.loads(report_path.read_text())
        actions = [json.loads(s) for s in (report_path.parent / "actions.jsonl").read_text().splitlines()]
        frames = [json.loads(s)["public_frame"] for s in (report_path.parent / "requests.jsonl").read_text().splitlines()]
        runs.append({"report": report, "actions": actions, "frames": frames})
    payload = json.dumps(runs).replace("<", "\\u003c")
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Tiny Aya · actual baseline traces</title><style>
body{font:16px system-ui;background:#10161e;color:#eef2f6;margin:0;padding:32px;max-width:1350px;margin:auto}
h1{font-size:28px}p{color:#b9c4d3;line-height:1.6}select,button{padding:10px;background:#202c3a;color:white;border:1px solid #708094;border-radius:6px}
input{width:65%;vertical-align:middle}#rooms{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}.room{padding:10px;border:1px solid #465369;border-radius:5px}.active{border-color:#ffbd69;background:#4c381f}.cleared{border-color:#77d6ac}
main{display:grid;grid-template-columns:1fr 1fr;gap:20px}pre{font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere;background:#17212e;padding:16px;border-radius:8px;max-height:560px;overflow:auto}
label{display:block;margin:12px 0}#scope{color:#ffcc85}details{margin-top:20px}@media(max-width:800px){main{display:block}body{padding:16px}}
</style><h1>Tiny Aya: actual baseline traces</h1><p>Frozen weights. Real local inference. Every displayed action and observation comes from a saved run. Assisted checkpoints are separate from unassisted performance.</p>
<label>Run <select id="run"></select></label><p id="scope"></p><div id="rooms"></div>
<button id="prev">Previous</button> <input id="step" type="range" min="0" value="0"> <button id="next">Next</button> <span id="counter"></span>
<main><section><h2>Model output</h2><pre id="model"></pre><h2>Result</h2><pre id="result"></pre></section><section><h2>Public state before action</h2><pre id="state"></pre></section></main>
<details><summary>Notebook at each actual wipe</summary><pre id="notebook"></pre></details>
<script id="data" type="application/json">PAYLOAD</script><script>
const data=JSON.parse(document.getElementById('data').textContent),el=id=>document.getElementById(id);
const names=['Dead or Alive','Switchboard','Tribunal','Distance','Balance','Witch Hunt','Osmosis'];
data.forEach((x,i)=>{const o=document.createElement('option');o.value=i;o.textContent=x.report.name;el('run').append(o)});
function draw(){const run=data[+el('run').value];if(!run)return;const r=run.report;el('step').max=Math.max(0,run.actions.length-1);const i=Math.min(+el('step').value,run.actions.length-1),a=run.actions[i];
el('scope').textContent=(r.assisted_prefix?'ASSISTED diagnostic — earlier actions/evidence supplied by legal reference prefix. ':'UNASSISTED episode from room 1. ')+(r.notebook_probe?'Reference completed room 3 objectives; model chose whether to write a notebook, then exited into an actual server restart. ':'')+'Outcome: '+r.reason+'.';
el('rooms').replaceChildren();names.forEach((n,j)=>{const x=document.createElement('span');x.className='room'+(a&&a.room===j+1?' active':'')+(!r.notebook_probe&&r.rooms_cleared_by_model.includes(j+1)?' cleared':'');x.textContent=(j+1)+' '+n;el('rooms').append(x)});
el('counter').textContent=a?'Action '+(i+1)+' / '+run.actions.length:'No completed model action';
el('model').textContent=a?a.raw:JSON.stringify(r.errors,null,2);el('result').textContent=a?JSON.stringify(a.output,null,2):'';el('state').textContent=JSON.stringify(run.frames[Math.max(0,i)]||{},null,2);el('notebook').textContent=JSON.stringify(r.wipes,null,2)}
el('run').onchange=()=>{el('step').value=0;draw()};el('step').oninput=draw;el('prev').onclick=()=>{el('step').value=Math.max(0,+el('step').value-1);draw()};el('next').onclick=()=>{el('step').value=Math.min(+el('step').max,+el('step').value+1);draw()};draw();
</script></html>'''.replace("PAYLOAD", payload)
    (BASE / "viewer.html").write_text(html)
    print(f"Saved viewer with {len(runs)} runs and {sum(len(r['actions']) for r in runs)} actual model actions")


if __name__ == "__main__":
    main()
