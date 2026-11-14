import argparse,hashlib,json
from baseline.paid.run import run_episode
from baseline.paid.config import ROOT,local_path
from borderland.env import BorderlandEnv
from .bridge import Ledger,Client,write,EFFORT,CAP

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true')
    parser.add_argument('--output',required=True);parser.add_argument('--ledger',required=True)
    parser.add_argument('--max-calls',type=int,choices=range(1,101),default=5,
                        metavar='1..100',help='Fixed attempt budget; cannot change an existing ledger')
    parser.add_argument('--resume',action='store_true',help='continue a paused episode in --output')
    parser.add_argument('--pause-after',type=int,default=None,help='seconds before pausing cleanly')
    parser.add_argument('--invalid-action',choices=['halt','error_frame'],default='halt')
    args=parser.parse_args();folder=local_path(args.output)
    resume=None
    if args.resume:
        resume=json.loads((folder/'actions.json').read_text()) if (folder/'actions.json').exists() else []
        if (folder/'report.json').exists():raise SystemExit('episode already finished')
    else:folder.mkdir(parents=True,exist_ok=False)
    ledger=Ledger(args.ledger,live=args.live,max_calls=args.max_calls)
    try:
        sources=list((ROOT/'baseline/codex_subscription').glob('*.py'))+list((ROOT/'borderland').glob('*.py'))+[
            ROOT/'baseline/paid/run.py',ROOT/'baseline/paid/guard.py',ROOT/'baseline/interface_v2.py',
            ROOT/'baseline/interface_v3.py',ROOT/'baseline/public_rules.txt']
        if not (folder/'run-contract.json').exists():write(folder/'run-contract.json',{'model':'gpt-6.1-terra','max_calls':args.max_calls,
            'mode':'live' if args.live else 'offline','reasoning_effort':EFFORT,'output_tokens_per_call':CAP,'invalid_action_policy':args.invalid_action,
            'public_request_byte_limit':64000,'no_progress_limit':3,'unassisted':True,
            'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}})
        world=json.loads((ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0/manifest.json').read_text())
        client=Client(ledger,folder,live=args.live)
        client.calls=len([d for d in folder.glob('call-*') if d.is_dir()])
        report=run_episode(BorderlandEnv(world=world),client,folder,
                           mode='native_codex_subscription_live' if args.live else 'native_codex_offline_fixture',
                           resume_actions=resume,pause_after_seconds=args.pause_after,invalid_action=args.invalid_action)
        print(json.dumps({k:report.get(k) for k in ['mode','actions','last_room','stop','success','wipes','exact_replay']},indent=2))
    finally:ledger.close()

if __name__=='__main__':main()
