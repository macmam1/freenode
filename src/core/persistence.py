import subprocess
import os
import json
from typing import Dict, Optional

class Persistence:
    """Backup FreeNode state to external storage (GitHub/Drive/S3)"""
    
    def __init__(self, state: dict = None):
        self.state = state or {}
        self.external_backends = ['github', 'drive', 's3']
    
    def backup(self, backend: str = 'github') -> bool:
        try:
            if backend == 'github':
                # Backup to GitHub via git commands
                subprocess.run(['git', 'add', 'freenode/state/'], check=True)
                subprocess.run(['git', 'commit', '-m', 'freenode: backup state'], check=True)
                subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)
                return True
            elif backend == 'drive':
                # Sync to Google Drive
                subprocess.run(['gdrive', 'sync'], check=True)
                return True
            elif backend == 's3':
                # Upload to S3
                import boto3
                s3 = boto3.client('s3')
                s3.upload_file('freenode/state/state.json', 'backup-bucket', 'state.json')
                return True
            return False
        except Exception as e:
            return False
    
    def load(self, backend: str = 'github') -> dict:
        try:
            if backend == 'github':
                result = subprocess.run(['git', 'show', 'HEAD:freenode/state/state.json'], capture_output=True, text=True)
                if result.returncode == 0:
                    return json.loads(result.stdout)
        except: pass
        return {}

if __name__ == "__main__":
    p = Persistence()
    print(p.backup('github'))
