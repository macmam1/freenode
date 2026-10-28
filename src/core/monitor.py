import time
import subprocess
import json
from typing import Dict, List
import psutil
import requests

class Monitor:
    """Self-monitoring + auto-revive for FreeNode modules"""
    
    def __init__(self, strategy: dict):
        self.strategy = strategy
        self.running_modules = []
        self.logs = []
    
    def start_all(self):
        self.logs.append({
            'event': 'start_all',
            'timestamp': time.time(),
            'modules': self.strategy.get('modules', []),
        })
        return self._check_module_health()
    
    def _check_module_health(self) -> Dict[str, bool]:
        health = {}
        for module in self.strategy.get('modules', []):
            health[module] = self._check_module(module)
        return health
    
    def _check_module(self, module: str) -> bool:
        try:
            if module == 'keepalive':
                # Check if keepalive is running
                result = subprocess.run(['pgrep', '-f', 'freenode.*keepalive'], capture_output=True)
                return result.returncode == 0
            elif module == 'tunnel':
                # Check tunnel process
                result = subprocess.run(['pgrep', '-f', 'cloudflared|freenode.*tunnel'], capture_output=True)
                return result.returncode == 0
            elif module == 'api':
                # Check API port
                for conn in psutil.net_connections():
                    if conn.status == 'ESTABLISHED' and conn.laddr and conn.laddr.port == 8000:
                        return True
            return False
        except:
            return False
    
    def auto_revive(self, module: str) -> bool:
        if module == 'keepalive':
            subprocess.Popen(['python', '-m', 'freenode.modules.keepalive.keepalive'], start_new_session=True)
        elif module == 'tunnel':
            subprocess.Popen(['python', '-m', 'freenode.modules.tunnel.cloudflare'], start_new_session=True)
        return True

if __name__ == "__main__":
    m = Monitor({})
    print(m.start_all())
