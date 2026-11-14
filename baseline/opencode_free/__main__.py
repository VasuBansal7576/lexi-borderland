import argparse
import json
from pathlib import Path
from baseline.paid.run import run_episode
from baseline.paid.config import ROOT, local_path
from borderland.env import BorderlandEnv
from .bridge import MODELS, Client, Ledger, write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', required=True)
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--models', nargs='+', choices=MODELS, default=list(MODELS))
    args = parser.parse_args()
    folder = local_path(args.output); folder.mkdir(parents=True,exist_ok=False)
    ledger = Ledger(args.ledger, live=args.live)
    world = json.loads((ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0/manifest.json').read_text())
    reports = []
    try:
        for model in dict.fromkeys(args.models):
            target = folder/model;target.mkdir()
            report = run_episode(BorderlandEnv(world=world), Client(model,ledger,target,live=args.live),
                                 target, mode='opencode_free_live' if args.live else 'opencode_offline_fixture')
            report['model'] = model
            reports.append({k:report[k] for k in ['model','mode','actions','last_room','stop','success','wipes','exact_replay']})
            write(folder/'summary.json', reports)
            print(json.dumps(reports[-1]),flush=True)
            # Global quota errors stop the entire sweep, not just the current model.
            if report['stop'] and ('429' in report['stop'] or 'free_usage_not_confirmed' in report['stop']): break
    finally: ledger.close()


if __name__ == '__main__': main()
