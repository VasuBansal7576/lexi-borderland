"""Sign in using the native official Codex client, with no model calls."""
import os
import subprocess
from .native import AUTH_STATE,make_state,environment,command

def main():
    os.umask(0o077)
    state=make_state(AUTH_STATE)
    args=command(state,login=True)+['-c','cli_auth_credentials_store="file"',
          '-c','forced_login_method="chatgpt"','login','--device-auth']
    subprocess.run(args,env=environment(state),cwd=state/'work',check=True)

if __name__=='__main__':main()
