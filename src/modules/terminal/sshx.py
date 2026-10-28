import subprocess
import json
import time
import os
import requests
from typing import Optional

class SSHXTerminal:
    """Web terminal module using sshx.io"""
    
    def __init__(self):
        self.api_base = "https://api.sshx.io/v1"
        self.session = None
    
    def start(self) -> dict:
        try:
            # Install sshx binary
            if not os.path.exists('/usr/local/bin/sshx'):
                subprocess.run(['curl', '-L', 'https://sshx.io/install.sh'], check=True)
            
            # Create session
            result = subprocess.Popen(
                ['sshx', 'share'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for session link
            time.sleep(3)
            output = result.stdout.read()
            for line in output.splitlines():
                if 'https://sshx.io/s/' in line:
                    session_url = line
                    return {'status': 'running', 'url': session_url, 'command': 'sshx share'}
            
            return {'status': 'failed', 'error': 'No session URL found'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    t = SSHXTerminal()
    print(json.dumps(t.start(), indent=2))
