import subprocess
import json
import os
import time
from typing import Optional, Dict

class CloudflareTunnel:
    """Cloudflare Tunnel module for FreeNode"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('CLOUDFLARE_TUNNEL_TOKEN')
        self.tunnel_name = "freenode"
    
    def start(self) -> dict:
        if not self.token:
            return {'status': 'failed', 'error': 'No CLOUDFLARE_TUNNEL_TOKEN provided'}
        
        try:
            # Install cloudflared
            if not os.path.exists('/usr/local/bin/cloudflared'):
                subprocess.run(['curl', '-L', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64', '-o', '/usr/local/bin/cloudflared'], check=True)
                subprocess.run(['chmod', '+x', '/usr/local/bin/cloudflared'], check=True)
            
            # Run tunnel
            cmd = ['cloudflared', 'tunnel', '--token', self.token, 'run', self.tunnel_name]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            
            time.sleep(2)
            return {'status': 'running', 'pid': proc.pid, 'command': ' '.join(cmd)}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    cf = CloudflareTunnel()
    print(json.dumps(cf.start(), indent=2))