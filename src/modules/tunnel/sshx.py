import subprocess
import json
import time
import os
from typing import Optional, Dict

class SSHXTunnel:
    """Reverse tunnel module using sshx.io for external access"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.session = None
    
    def start(self) -> dict:
        try:
            if not os.path.exists('/usr/local/bin/sshx'):
                subprocess.run(['curl', '-sSL', 'https://sshx.io/install.sh', '|', 'sh'], shell=True, check=True)
            
            # Create reverse tunnel
            cmd = ['sshx', 'share', '--remote', f'localhost:{self.port}', '--name', 'freenode']
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
            
            time.sleep(4)
            url = None
            output = proc.stdout.read()
            for line in output.splitlines():
                if 'sshx.io' in line:
                    url = line.strip()
                    break
            
            return {
                'status': 'running' if url else 'failed',
                'pid': proc.pid,
                'url': url,
                'local_port': self.port,
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    t = SSHXTunnel(port=8000)
    print(json.dumps(t.start(), indent=2))
