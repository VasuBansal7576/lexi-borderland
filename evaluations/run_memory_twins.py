"""Balanced wipe diagnostics: do not mistake one lucky empty-note guess for memory."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baseline.run import Server,write
from baseline.run_v2 import evaluate

def main():
    folder=ROOT/'artifacts/model-interface-v2/memory-balanced'
    folder.mkdir(parents=True,exist_ok=False)
    server=Server(folder);reports=[]
    try:
        for phase,sigma in ((0,0),(0,1),(1,0),(1,1)):
            source=ROOT/f'artifacts/certification-v1/family-0000/phase-{phase}-sigma-{sigma}'
            reports.append(evaluate(server,f'memory-p{phase}-s{sigma}',source,room=3,memory=True))
    finally:
        server.stop();write(folder/'summary.json',reports)

if __name__=='__main__':main()
