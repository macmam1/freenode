import json
from typing import Dict, List, Optional

class Profiler:
    """Generate platform profiles from detector results"""
    
    PLATFORM_CLASSES = {
        'containerized_free': ['render', 'railway', 'fly', 'koyeb', 'glitch', 'snapdeploy', 'freestyle', 'runloop', 'clever', 'serverix', 'replit'],
        'notebook_hosted': ['colab', 'kaggle', 'molab', 'deepnote', 'datalore', 'gradient', 'saturn', 'chainide'],
        'serverless_edge': ['vercel', 'netlify', 'cloudflare_workers', 'supabase', 'firebase', 'deno_deploy', 'wasmer', 'fleek'],
        'micro_vm': ['oracle_cloud', 'gcp', 'aws', 'azure', 'codespaces', 'gitpod', 'stackblitz', 'codesandbox', 'daytona', 'e2b'],
        'real_vms': ['oracle', 'gcp', 'aws', 'azure', 'vultr', 'digitalocean', 'alibaba', 'google_cloud'],
        'saas_hosted': ['belmo', 'stormkit', 'qoddi', 'zeabur', 'encore', 'apply_build', 'tiiny', 'kinsta', 'nhost', 'ninox', 'back4app', '8base', 'appwrite', 'aiven', 'cockroachlabs'],
        'static_only': ['infinityfree', 'awardspace', 'pythonanywhere', 'val_town', 'codeberg', 'boxd', 'static_hosting'],
    }
    
    def __init__(self, detector_results: dict):
        self.detector_results = detector_results
        self.platform = self._detect_platform(detector_results)
        self.limits = self._detect_limits(detector_results)
        self.profile = self._generate_profile()
    
    def _detect_platform(self, r: dict) -> str:
        env_str = str(r)
        if 'COLAB_GPU' in env_str: return 'colab'
        if 'KAGGLE' in env_str: return 'kaggle'
        if 'MOLAB' in env_str: return 'molab'
        if 'RENDER' in env_str: return 'render'
        if 'RAILWAY' in env_str: return 'railway'
        if 'KOYEB' in env_str: return 'koyeb'
        if 'GLITCH' in env_str: return 'glitch'
        if 'SNAPDEPLOY' in env_str: return 'snapdeploy'
        if 'ORACLE' in env_str: return 'oracle_cloud'
        if 'AWS' in env_str: return 'aws'
        if 'GCP' in env_str: return 'gcp'
        if 'AZURE' in env_str: return 'azure'
        if 'OPENAI_API_KEY' in env_str or 'ANTHROPIC_API_KEY' in env_str: return 'local_llm'
        return 'unknown'
    
    def _detect_limits(self, r: dict) -> dict:
        limits = {
            'sleep_minutes': 0,
            'session_hours': 0,
            'timeout_seconds': 0,
            'ram_gb': round(float(self.detector_results.get('memory_total', 0)), 2),
            'disk_gb': round(float(self.detector_results.get('disk_total', 0)), 2),
            'cpu_cores': int(self.detector_results.get('cpu_count', 0)),
            'is_root': bool(self.detector_results.get('is_root', False)),
            'is_container': bool(self.detector_results.get('is_container', False)),
            'is_notebook': self._is_notebook(r),
            'is_serverless': self._is_serverless(r),
        }
        return limits
    
    def _is_notebook(self, r: dict) -> bool:
        s = str(r)
        return any(k in s for k in ['COLAB', 'KAGGLE', 'MOLAB', 'NOTEBOOK', 'JUPYTER', 'DEEPNOTE', 'DATALORE', 'CHAINIDE'])
    
    def _is_serverless(self, r: dict) -> bool:
        s = str(r)
        return any(k in s for k in ['VERCEL', 'NETLIFY', 'FUNCTION', 'EDGE', 'WORKER', 'STATIC', 'SERVERLESS'])
    
    def _generate_profile(self) -> dict:
        env_class = self._get_class()
        return {
            'platform': self.platform,
            'class': env_class,
            'limits': self.limits,
            'modules': self._select_modules(env_class),
            'strategy': f"{self.platform}:{env_class}",
        }
    
    def _get_class(self) -> str:
        r = self.detector_results
        if self._is_notebook(r): return 'notebook_hosted'
        if self._is_serverless(r): return 'serverless_edge'
        if self.limits['is_container']: return 'containerized_free'
        if not self.limits['is_root'] and not self.limits['is_container']: return 'real_vms'
        return 'unknown'
    
    def _select_modules(self, env_class: str) -> list:
        modules_map = {
            'containerized_free': ['keepalive', 'tunnel', 'api', 'terminal'],
            'notebook_hosted': ['keepalive', 'tunnel', 'api', 'terminal', 'ssh', 'persistence'],
            'serverless_edge': ['api', 'tunnel'],
            'real_vms': ['tunnel', 'ssh', 'api', 'terminal'],
            'micro_vm': ['tunnel', 'ssh', 'api', 'terminal', 'resource'],
            'saas_hosted': ['tunnel', 'ssh', 'api', 'terminal'],
            'static_only': ['tunnel'],
            'unknown': ['keepalive', 'tunnel', 'api'],
        }
        return modules_map.get(env_class, ['keepalive', 'tunnel', 'api'])
