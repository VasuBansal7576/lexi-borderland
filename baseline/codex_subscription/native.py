"""Official Codex CLI only. Project-local state, never the user's global auth."""
import sys
from pathlib import Path
from baseline.paid.config import ROOT, local_path

BASE=ROOT/'runtime/codex-subscription'
INSTALL=BASE/'native-client'
BINARY=INSTALL/'package/vendor/aarch64-apple-darwin/bin/codex'
LINUX=sys.platform.startswith('linux')
INSTALL_LINUX=BASE/'native-client-linux'
BINARY_LINUX=INSTALL_LINUX/'package/vendor/aarch64-unknown-linux-musl/bin/codex'
# Per-call state holds a temporary login copy that must be deleted after each call. The Cowork
# mount forbids deletion, so on Linux per-call state lives in VM-local storage outside Lexi.
CALLS=(Path.home()/'.lexi-codex-calls') if LINUX else BASE/'calls'
AUTH_STATE=BASE/'native-auth'
MODEL='gpt-6.1-terra'

def make_state(path):
    path=Path(path).resolve() if (LINUX and Path(path).resolve().is_relative_to(CALLS)) else local_path(path)
    for directory in ['work','state','tmp','config','cache','data']:
        (path/directory).mkdir(parents=True,exist_ok=True,mode=0o700)
    return path

def environment(path):
    # Configure the documented Codex state location; no global credentials are inherited.
    codex_state_dir=path/'state'
    return {'PATH':'/usr/bin:/bin','CODEX_HOME':str(codex_state_dir),
            'TMPDIR':str(path/'tmp'),'XDG_CONFIG_HOME':str(path/'config'),
            'XDG_CACHE_HOME':str(path/'cache'),'XDG_DATA_HOME':str(path/'data')}

def profile(path, *, login=False, relay_port=None):
    path=local_path(path)
    network='' if login else ('(deny network*)' if relay_port is None else
        f'(deny network-outbound (require-not (remote ip "localhost:{relay_port}")))\n(deny network-inbound)')
    return f'''(version 1)
(allow default)
{network}
(deny file-read-data (require-all
 (require-not (subpath "{path}")) (require-not (subpath "{INSTALL}"))
 (require-any (subpath "/Users") (subpath "/Volumes")
 (subpath "/private/var/folders") (subpath "/var/folders")
 (subpath "/private/tmp") (subpath "/tmp")
 (subpath "/Library/Application Support") (subpath "/Library/Managed Preferences"))))
(deny file-write* (require-not (subpath "{path}")))
'''

def command(path, *, login=False, relay_port=None):
    if LINUX:
        # Linux (Cowork VM): bubblewrap hides the user's home and project, including the master
        # login cache and earlier call directories; only this call's state and the official
        # client are visible. Network is NOT namespace-restricted here (the relay listens on host
        # loopback); the client is configured to talk only to the local relay.
        path=Path(path).resolve()
        return ['bwrap','--ro-bind','/','/','--dev','/dev','--proc','/proc','--tmpfs',str(Path.home()),
                '--bind',str(path),str(path),'--ro-bind',str(INSTALL_LINUX),str(INSTALL_LINUX),
                '--die-with-parent',str(BINARY_LINUX)]
    target=path/'sandbox.sb';target.write_text(profile(path,login=login,relay_port=relay_port))
    return ['/usr/bin/sandbox-exec','-f',str(target),str(BINARY)]
