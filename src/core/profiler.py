import json
from typing import Dict, List, Optional

class Profiler:
    """Generate platform profiles from detector results"""
    
    # Platform classification
    PLATFORM_CLASSES = {
        'containerized_free': ['render', 'railway', 'fly', 'koyeb', 'glitch', 'snapdeploy', 'freestyle', 'runloop', 'clever', 'serverix', 'replit', 'glitch'],
        'notebook_hosted': ['colab', 'kaggle', 'molab', 'deepnote', 'datalore', 'gradient', 'saturn'],
        'serverless_edge': ['vercel', 'netlify', 'cloudflare_workers', 'supabase', 'firebase', 'deno_deploy', 'wasmer', 'fleek'],
        'micro_vm': ['oracle_cloud', 'gcp', 'aws', 'azure', 'codespaces', 'gitpod', 'stackblitz', 'codesandbox'],
        'real_vms': ['oracle_cloud', 'gcp', 'aws', 'azure', 'google_cloud', 'aws_ec2', 'vultr', 'digitalocean', 'alibaba'],
        'saas_hosted': ['belmo', 'stormkit', 'qoddi', 'zeabur', 'encore', 'apply_build', 'tiiny', 'kinsta', 'nhost', '8base', 'back4app', 'ninox'],
        'static_only': ['infinityfree', 'awardspace', 'pythonanywhere', 'val_town', 'codeberg', 'boxd', 'static_hosting', 'netlify', 'vercel'],
    }
    
    def __init__(self, detector_results: dict):
        self.detector_results = detector_results
        self.platform = self.detect_platform(detector_results)
        self.limits = self.detect_limits(detector_results)
        self.profile = self.generate_profile()
    
    def detect_platform(self, r: dict) -> str:
        env_str = str(r)
        if 'COLAB_GPU' in env_str: return 'colab'
        if 'KAGGLE' in env_str: return 'kaggle'
        if 'RENDER' in env_str: return 'render'
        if 'RAILWAY' in env_str: return 'railway'
        if 'KOYEB' in env_str: return 'koyeb'
        if 'GLITCH' in env_str: return 'glitch'
        if 'SNAPDEPLOY' in env_str: return 'snapdeploy'
        if 'FREE' in env_str and 'MEMORY' in env_str: return 'generic_free'
        if 'OPENAI_API_KEY' in env_str or 'ANTHROPIC_API_KEY' in env_str: return 'local_llm'
        return 'unknown'
    
    def detect_limits(self, r: dict) -> dict:
        limits = {}
        limits['sleep_minutes'] 0 if 'sleep' not in str(r).lower() else self._parse_sleep(r)
        limits['session_hours'] 0 if 'session' not in str(r).lower() else self._parse_session(r)
        limits['timeout_seconds'] 0 if 'timeout' not in str(r).lower() else self._parse_timeout(r)
        limits['ram_gb'] int(self.detector_results.get('memory_total', 0))
        limits['disk_gb'] int(self.detector_results.get('disk_total', 0))
        limits['cpu_cores'] int(self.detector_results.get('cpu_count', 0))
        limits['is_root'] bool(self.detector_results.get('is_root', False))
        limits['is_container'] bool(self.detector_results.get('is_container', False))
        limits['is_notebook'] bool(self._is_notebook(r))
        limits['is_serverless'] bool(self._is_serverless(r))
        return limits
    
    def _parse_sleep(self, r: dict) -> int:
        try:
            for v in str(r.values()):
                if 'sleep' in str(v).lower():
                    num = ''.join(c for c in str(v) if c.isdigit())
                    if num: return int(num)
        except: pass
        return 0
    
    def _parse_session(self, r: dict) -> int:
        return 0
    
    def _parse_timeout(self, r: dict) -> int:
        return 0
    
    def _is_notebook(self, r: dict) -> bool:
        s = str(r)
        return any(k in s for k in ['COLAB', 'KAGGLE', 'MOLAB', 'NOTEBOOK', 'JUPYTER', 'DEEPNOTE'])
    
    def _is_serverless(self, r: dict) -> bool:
        s = str(r)
        return any(k in s for k in ['SERVERLESS', 'FUNCTION', 'EDGE', 'WORKER', 'STATIC'])
    
    def generate_profile(self) -> dict:
        profile = {
            'platform': self.platform,
            'environment': self.detector_results,
            'limits': self.limits,
            'class': self._get_class(),
            'modules': self._select_modules(),
            'strategy': self._get_strategy(),
        }
        return profile
    
    def _get_class(self) -> str:
        r = self.detector_results
        if self.is_notebook(r): return 'notebook_hosted'
        if self._is_serverless(r): return 'serverless_edge'
        if self.limits['is_container'] and not self.is_notebook(r): return 'containerized_free'
        if not self.limits['is_container']: return 'real_vms' if not self.limits['is_root'] else 'micro_vm'
        return 'unknown'
    
    def _select_modules(self) -> list:
        cls = self._get_class()
        modules_map = {
            'containerized_free': ['keepalive', 'tunnel', 'api', 'terminal'],
            'notebook_hosted': ['keepalive', 'tunnel', 'api', 'terminal', 'ssh', 'persistence'],
            'serverless_edge': ['api', 'tunnel', 'resource'],
            'real_vms': ['tunnel', 'ssh', 'api', 'terminal'],
            'micro_vm': ['tunnel', 'ssh', 'api', 'terminal', 'resource'],
            'saas_hosted': ['tunnel', 'ssh', 'api', 'terminal'],
            'static_only': ['tunnel'],
        }
        return modules_map.get(cls, ['keepalive', 'tunnel', 'api', 'terminal'])
    
    def _get_strategy(self) -> str:
        return f"{self.platform}:{self._get_class()}"
