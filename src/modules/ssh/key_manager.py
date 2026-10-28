"""
SSH Key Manager — Generate, persist, and manage SSH keys
"""

import subprocess
import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict

class KeyManager:
    """Manage SSH keys for FreeNode"""

    def __init__(self):
        self.ssh_dir = Path("~/.ssh/").expanduser()
        self.ssh_dir.mkdir(parents=True, exist_ok=True)
        self.key_name = "freenode_id_rsa"
        self.key_path = self.ssh_dir / self.key_name
        self.pubkey_path = self.ssh_dir / f"{self.key_name}.pub"
        self.authorized_keys = self.ssh_dir / "authorized_keys"

    def generate(self, bits: int = 2048, comment: str = "freenode@host") -> dict:
        """Generate new SSH key pair"""
        if self.key_path.exists():
            return {"status": "exists", "message": "Key already exists"}

        try:
            subprocess.run(
                ["ssh-keygen", "-t", "rsa", "-b", str(bits), "-f", str(self.key_path), "-N", "", "-C", comment],
                check=True,
                capture_output=True
            )
            self.key_path.chmod(0o600)
            self.pubkey_path.chmod(0o644)
            return {
                "status": "ok",
                "key_path": str(self.key_path),
                "pubkey_path": str(self.pubkey_path),
                "fingerprint": self.fingerprint(),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fingerprint(self) -> str:
        """Get fingerprint of current key"""
        if not self.key_path.exists():
            return ""
        try:
            result = subprocess.run(
                ["ssh-keygen", "-l", "-f", str(self.key_path)],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return ""

    def get_public_key(self) -> str:
        """Read public key content"""
        if not self.pubkey_path.exists():
            return ""
        return self.pubkey_path.read_text().strip()

    def get_private_key(self) -> str:
        """Read private key content"""
        if not self.key_path.exists():
            return ""
        return self.key_path.read_text().strip()

    def add_authorized(self, pubkey: str) -> bool:
        """Add a public key to authorized_keys"""
        try:
            existing = set()
            if self.authorized_keys.exists():
                existing = set(self.authorized_keys.read_text().strip().splitlines())
            if pubkey not in existing:
                with open(self.authorized_keys, "a") as f:
                    f.write(pubkey + "\n")
            self.authorized_keys.chmod(0o600)
            return True
        except Exception as e:
            return False

    def remove_authorized(self, pubkey: str) -> bool:
        """Remove a public key from authorized_keys"""
        try:
            if not self.authorized_keys.exists():
                return False
            lines = self.authorized_keys.read_text().strip().splitlines()
            lines = [l for l in lines if l != pubkey]
            self.authorized_keys.write_text("\n".join(lines) + "\n")
            return True
        except:
            return False

    def list_keys(self) -> List[Dict[str, str]]:
        """List all SSH keys in ~/.ssh/"""
        keys = []
        if not self.ssh_dir.exists():
            return keys
        for f in self.ssh_dir.glob("*.pub"):
            try:
                content = f.read_text().strip()
                keys.append({
                    "name": f.name,
                    "path": str(f),
                    "content": content,
                    "type": content.split()[0],
                })
            except:
                pass
        return keys

    def persist(self) -> bool:
        """Persist keys to external storage (GitHub/Drive/S3)"""
        try:
            # Write to state directory
            state_dir = Path("~/.freenode/state/").expanduser()
            state_dir.mkdir(parents=True, exist_ok=True)
            state_file = state_dir / "ssh_keys.json"

            data = {
                "private_key": self.get_private_key(),
                "public_key": self.get_public_key(),
                "fingerprint": self.fingerprint(),
            }

            state_file.write_text(json.dumps(data, indent=2))
            state_file.chmod(0o600)
            return True
        except Exception as e:
            return False

    def load(self) -> Optional[Dict[str, str]]:
        """Load keys from external storage"""
        try:
            state_file = Path("~/.freenode/state/ssh_keys.json").expanduser()
            if not state_file.exists():
                return None
            data = json.loads(state_file.read_text())
            # Write back to SSH directory
            if data.get("private_key"):
                self.key_path.write_text(data["private_key"])
                self.key_path.chmod(0o600)
            if data.get("public_key"):
                self.pubkey_path.write_text(data["public_key"])
                self.pubkey_path.chmod(0o644)
            return data
        except Exception as e:
            return None