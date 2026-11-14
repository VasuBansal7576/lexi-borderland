"""Isolated observation-only solver worker; no environment imports permitted."""

import hashlib
import json
import os
from pathlib import Path
import sys


def main():
    folder = Path(__file__).resolve().parent
    # Load only public reasoning code before permanently disabling file access.
    sys.path.insert(0, str(folder))
    import mechanics
    import planning
    import solver
    code_hashes = {name: hashlib.sha256((folder / f"{name}.py").read_bytes()).hexdigest()
                   for name in ("mechanics", "planning", "solver")}
    sys.path.remove(str(folder))
    def audit(event, args):
        if event in ("open", "os.listdir", "os.scandir", "os.chdir", "os.system", "subprocess.Popen", "ctypes.dlopen") or event.startswith(("socket.", "os.exec", "os.spawn")):
            raise PermissionError(f"evidence-only worker forbids {event}")
    sys.addaudithook(audit)
    blocked = []
    for filename in (folder / "world.py", folder.parent / "00-IDEA.md"):
        try:
            with open(filename):
                pass
        except PermissionError:
            blocked.append(filename.name)
        else:
            raise RuntimeError("worker isolation failed")
    policy = solver.EvidenceSolver()
    print(json.dumps({"hello": True, "pid": os.getpid(), "code_hashes": code_hashes,
                      "private_read_probes_blocked": blocked,
                      "private_modules_loaded": [name for name in sys.modules if name in ("world", "env", "borderland.world", "borderland.env")]}), flush=True)
    for line in sys.stdin:
        try:
            message = json.loads(line)
            action = policy.act(message)
            print(json.dumps({"action": action, "diagnostics": policy.diagnostics}, separators=(",", ":")), flush=True)
        except Exception as exc:
            print(json.dumps({"error": type(exc).__name__ + ": " + str(exc), "diagnostics": policy.diagnostics}), flush=True)
            break


if __name__ == "__main__":
    main()
