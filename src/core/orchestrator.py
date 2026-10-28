from typing import Dict, List, Optional
import json

class Orchestrator:
    """Selects strategy modules based on platform profile"""
    
    def __init__(self, profile: dict):
        self.profile = profile
        self.modules = []
        self.strategy = self._build_strategy()
    
    def _build_strategy(self) -> dict:
        platform = self.profile.get('platform', 'unknown')
        env_class = self.profile.get('class', 'unknown')
        modules_needed = self.profile.get('modules', ['keepalive', 'tunnel', 'api', 'terminal'])
        
        strategy = {
            'platform': platform,
            'environment_class': env_class,
            'modules': modules_needed,
            'keepalive_enabled': self._should_enable('keepalive', env_class),
            'tunnel_enabled': self._should_enable('tunnel', env_class),
            'ssh_enabled': self._should_enable('ssh', env_class),
            'terminal_enabled': self._should_enable('terminal', env_class),
            'api_enabled': self._should_enable('api', env_class),
            'resource_bypass_enabled': self._should_enable('resource', env_class),
            'privilege_escalation': env_class not in ['real_vms', 'micro_vm'],
        }
        return strategy
    
    def _should_enable(self, module: str, env_class: str) -> bool:
        modules_map = {
            'keepalive': True,
            'tunnel': True,
            'ssh': True,
            'terminal': True,
            'api': True,
            'resource': False,
            'privilege': True,
        }
        return modules_map.get(module, False)
    
    def generate_commands(self) -> Dict[str, List[str]]:
        strategy = self.strategy
        commands = {}
        
        if strategy['keepalive_enabled']:
            commands['keepalive'] = [
                "freenode keepalive enable --strategy http_ping --interval 600",
                "freenode keepalive enable --strategy traffic_gen --target health_check",
            ]
        
        if strategy['tunnel_enabled']:
            commands['tunnel'] = [
                "freenode tunnel enable --provider sshx --priority 1",
                "freenode tunnel enable --provider cloudflare --priority 2",
                "freenode tunnel enable --provider frp --priority 3",
                "freenode tunnel enable --provider ngrok --priority 4",
            ]
        
        if strategy['ssh_enabled']:
            commands['ssh'] = [
                "freenode ssh install --method dropbear",
                "freenode ssh key generate --alias freenode-key",
            ]
        
        if strategy['terminal_enabled']:
            commands['terminal'] = [
                "freenode terminal enable --backend sshx",
                "freenode terminal enable --backend ttyd",
            ]
        
        if strategy['api_enabled']:
            commands['api'] = [
                "freenode api start --port 8000",
            ]
        
        if strategy['resource_bypass_enabled']:
            commands['resource'] = [
                "freenode resource enable --method proot",
            ]
        
        return commands

    def full_strategy(self) -> dict:
        return {
            'profile': self.profile,
            'strategy': self.strategy,
            'commands': self.generate_commands(),
        }
