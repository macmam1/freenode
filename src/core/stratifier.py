import json
import os

class Stratifier:
    """Maps platform → environment class for strategy selection"""
    
    PLATFORM_CLASSES = {
        # Class: Containerized Free (sleep/time-limited containers)
        'containerized': [
            'render', 'railway', 'fly', 'koyeb', 'glitch', 'snapdeploy',
            'freestyle', 'runloop', 'clever', 'serverix', 'replit',
            'heliohost', 'alwaysdata', 'awardspace', 'infinityfree',
            'cpanelfree', 'wispbyte', 'atyro', 'lucity', 'pella',
            'superve', 'zeabur', 'qoddi', 'stormkit', 'belmo',
            'kubeletto', 'hopx', 'rdphostings',
        ],
        
        # Class: Notebook-Hosted (session-based GPU/compute)
        'notebook': [
            'colab', 'kaggle', 'molab', 'deepnote', 'datalore',
            'gradient', 'saturn', 'binder', 'chainide',
        ],
        
        # Class: Serverless / Edge (stateless compute with timeout)
        'serverless': [
            'vercel', 'netlify', 'cloudflare_workers', 'deno_deploy',
            'supabase', 'firebase', 'wasmer', 'fleek', 'val_town',
        ],
        
        # Class: Micro-VM / Sandbox (session-based, limited control)
        'microvm': [
            'codespaces', 'gitpod', 'stackblitz', 'codesandbox',
            'daytona', 'e2b', 'boxd',
        ],
        
        # Class: Real VM / Permanent (no sleep, real resources)
        'realvm': [
            'oracle_cloud', 'gcp', 'aws', 'azure', 'vultr',
            'digitalocean', 'alibaba', 'google_cloud', 'aws_ec2',
            'ibmq', 'ibm_cloud',
        ],
        
        # Class: SaaS / Always-On (managed, no sleep)
        'saas': [
            'belmo', 'stormkit', 'qoddi', 'zeabur', 'encore',
            'apply_build', 'tiiny', 'kinsta', 'nhost', 'ninox',
            'back4app', '8base', 'appwrite', 'aiven', 'cockroachlabs',
            'clevcl', 'clear', 'hopsworks', 'runkoda', 'openship',
            'vibenest', 'botkeep', 'livemy', 'superserve', 'katabump',
            'cloud_dada', 'lucity', 'athyro', 'serverix', 'open_claw',
            'prepare', 'datadog', 'grafana',
        ],
        
        # Class: CI/CD (time-limited jobs)
        'cicd': [
            'github_actions', 'gitlab_ci', 'circleci', 'buddy',
            'buildkite', 'semaphore', 'appcircle', 'codeberg',
        ],
        
        # Class: Static Only (no compute)
        'static': [
            'infinityfree', 'awardspace', 'pythonanywhere',
            'val_town', 'codeberg', 'boxd', 'static_hosting',
        ],
    }
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name.lower()
        self.env_class = self._classify()
    
    def _classify(self) -> str:
        for cls, platforms in self.PLATFORM_CLASSES.items():
            if any(p in self.platform_name for p in platforms):
                return cls
        return 'unknown'
    
    def get_modules(self) -> list:
        class_modules = {
            'containerized': ['keepalive', 'tunnel', 'api', 'terminal'],
            'notebook': ['keepalive', 'tunnel', 'api', 'terminal', 'ssh', 'persistence'],
            'serverless': ['api', 'tunnel'],
            'microvm': ['tunnel', 'api', 'terminal', 'persistence'],
            'realvm': ['tunnel', 'ssh', 'api', 'terminal'],
            'saas': ['tunnel', 'ssh', 'api', 'terminal'],
            'cicd': ['tunnel', 'persistence'],
            'static': ['tunnel'],
            'unknown': ['keepalive', 'tunnel', 'api', 'terminal'],
        }
        return class_modules.get(self.env_class, [])
    
    def get_tunnel_priority(self) -> list:
        priority = {
            'containerized': ['cloudflare', 'sshx', 'frp', 'ngrok'],
            'notebook': ['sshx', 'frp', 'cloudflare', 'ngrok'],
            'serverless': ['cloudflare', 'ngrok'],
            'microvm': ['sshx', 'cloudflare'],
            'realvm': ['cloudflare', 'sshx'],
            'saas': ['cloudflare', 'sshx'],
            'cicd': ['sshx', 'frp'],
            'static': ['cloudflare'],
            'unknown': ['cloudflare', 'sshx', 'frp', 'ngrok'],
        }
        return priority.get(self.env_class, ['cloudflare', 'sshx'])
    
    def get_keepalive_interval(self) -> int:
        intervals = {
            'containerized': 600,  # 10 min (sleep at 15 min → ping at 10 min)
            'notebook': 660,       # 11 min (session at 12h → ping at 11h)
            'serverless': 0,       # No keepalive
            'microvm': 300,       # 5 min (session shorter)
            'realvm': 0,          # No keepalive
            'saas': 0,            # No keepalive
            'cicd': 3300,         # 55 min (job at 1h)
            'static': 0,
            'unknown': 600,
        }
        return intervals.get(self.env_class, 600)
    
    def full_profile(self) -> dict:
        return {
            'platform': self.platform_name,
            'class': self.env_class,
            'modules': self.get_modules(),
            'tunnel_priority': self.get_tunnel_priority(),
            'keepalive_interval': self.get_keepalive_interval(),
        }


# Platform strategies registry (source of truth)
def load_platform_strategies() -> dict:
    return {
        'render': {
            'class': 'containerized',
            'modules': ['keepalive', 'tunnel', 'api'],
            'tunnel': ['sshx', 'cloudflare'],
            'keepalive_interval': 600,
            'sleep_minutes': 15,
            'notes': 'Use http_ping to /health endpoint',
        },
        'railway': {
            'class': 'containerized',
            'modules': ['keepalive', 'tunnel', 'api'],
            'tunnel': ['sshx', 'frp'],
            'keepalive_interval': 660,
            'credit_limit': 5,
            'notes': 'Credit optimizer needed',
        },
        'koyeb': {
            'class': 'containerized',
            'modules': ['tunnel', 'api'],
            'tunnel': ['cloudflare', 'sshx'],
            'keepalive_interval': 0,
            'notes': 'No sleep limit, but tunnel needed for external access',
        },
        'glitch': {
            'class': 'containerized',
            'modules': ['keepalive', 'tunnel'],
            'tunnel': ['localtunnel', 'ngrok'],
            'keepalive_interval': 240,
            'sleep_minutes': 5,
            'notes': 'Very short sleep, use fast pinging',
        },
        'colab': {
            'class': 'notebook',
            'modules': ['keepalive', 'tunnel', 'ssh', 'persistence'],
            'tunnel': ['sshx', 'cloudflare'],
            'keepalive_interval': 660,
            'session_hours': 12,
            'notes': 'Use activity simulation + Drive sync',
        },
        'kaggle': {
            'class': 'notebook',
            'modules': ['keepalive', 'tunnel', 'persistence'],
            'tunnel': ['sshx', 'frp'],
            'keepalive_interval': 3600,
            'session_hours': 30,
            'notes': 'Weekly limit, smart scheduling needed',
        },
        'molab': {
            'class': 'notebook',
            'modules': ['keepalive', 'tunnel', 'ssh', 'persistence'],
            'tunnel': ['sshx', 'frp', 'cloudflare'],
            'keepalive_interval': 600,
            'notes': 'Kernel can die, use kernel-independent SSH',
        },
        'oracle_cloud': {
            'class': 'realvm',
            'modules': ['tunnel', 'ssh', 'api', 'terminal'],
            'tunnel': ['cloudflare', 'sshx'],
            'keepalive_interval': 0,
            'notes': 'Always-on, real resources. Setup cloudflared as daemon',
        },
        'cloudflare_workers': {
            'class': 'serverless',
            'modules': ['api', 'tunnel'],
            'tunnel': ['workers_relay'],
            'keepalive_interval': 0,
            'timeout_ms': 50,
            'notes': 'Use multi-worker chain for long tasks',
        },
        'vercel': {
            'class': 'serverless',
            'modules': ['api', 'tunnel'],
            'tunnel': ['external_relay'],
            'keepalive_interval': 0,
            'timeout_seconds': 15,
            'notes': 'Edge function → external backend relay',
        },
        'belmo': {
            'class': 'saas',
            'modules': ['tunnel', 'ssh', 'api'],
            'tunnel': ['direct'],
            'keepalive_interval': 0,
            'notes': 'Always-on, use auto token capture',
        },
        'stormkit': {
            'class': 'saas',
            'modules': ['tunnel', 'api'],
            'tunnel': ['direct'],
            'keepalive_interval': 0,
            'notes': 'No sleep, tunnel for external access',
        },
        'freestyle': {
            'class': 'containerized',
            'modules': ['keepalive', 'tunnel', 'api'],
            'tunnel': ['sshx', 'frp'],
            'keepalive_interval': 600,
            'notes': 'Deploy-only, need git→API relay',
        },
        'e2b': {
            'class': 'microvm',
            'modules': ['tunnel', 'persistence'],
            'tunnel': ['sshx'],
            'keepalive_interval': 300,
            'notes': 'Sandbox VM, external persistence needed',
        },
        'github_actions': {
            'class': 'cicd',
            'modules': ['tunnel', 'persistence'],
            'tunnel': ['sshx'],
            'keepalive_interval': 3300,
            'job_hours': 6,
            'notes': 'Use artifact storage + self-hosted runner',
        },
    }
