"""
SSH Server Module — Dropbear & OpenSSH Auto-Installer
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Optional, List
import shutil

class SSHD:
    """Install and manage SSH server on current platform"""

    def __init__(self):
        self.ssh_key_path = Path("~/.ssh/freenode_id_rsa").expanduser()
        self.authorized_keys = Path("~/.ssh/authorized_keys").expanduser()
        self.config_dir = Path("~/.freenode/ssh/").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def install(self, method: str = "dropbear") -> dict:
        """Install SSH server via package manager or static binary"""
        results = {"status": "ok", "method": method, "actions": []}

        try:
            if method == "dropbear":
                results["actions"].append(self._install_dropbear())
            elif method == "openssh":
                results["actions"].append(self._install_openssh())
            else:
                results["status"] = "error"
                results["message"] = "Unknown method"
                return results
        except Exception as e:
            results["status"] = "error"
            results["message"] = str(e)
            return results

        return results

    def _install_dropbear(self) -> str:
        """Install Dropbear SSH server"""
        check = shutil.which("dropbear")
        
        if not check:
            # Try system package manager
            if shutil.which("apt-get"):
                subprocess.run(["apt-get", "install", "-y", "dropbear"], check=True)
            elif shutil.which("yum"):
                subprocess.run(["yum", "install", "-y", "dropbear"], check=True)
            elif shutil.which("apk"):
                subprocess.run(["apk", "add", "dropbear"], check=True)
            else:
                # Download static binary
                url = "https://github.com/mkj/dropbear/releases/download/BLOWFISH_2019.78-1/dropbear-linux-static"
                subprocess.run(["curl", "-L", "-o", "/usr/local/bin/dropbear", url], check=True)
                subprocess.run(["chmod", "+x", "/usr/local/bin/dropbear"], check=True)

        # Create host key
        host_key_path = str(self.config_dir / "dropbear_rsa_host_key")
        if not os.path.exists(host_key_path):
            subprocess.run(["dropbearkey", "-t", "rsa", "-f", host_key_path], check=True)

        # Start SSH server on port 22 (or random port if 22 taken)
        port = self._find_free_port(22)
        proc = subprocess.Popen(
            ["dropbear", "-E", "-F", "-p", str(port), "-r", host_key_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return f"Dropbear started on port {port} (PID: {proc.pid})"

    def _install_openssh(self) -> str:
        """Install OpenSSH server"""
        check = shutil.which("sshd")

        if not check:
            if shutil.which("apt-get"):
                subprocess.run(["apt-get", "install", "-y", "openssh-server"], check=True)
            elif shutil.which("yum"):
                subprocess.run(["yum", "install", "-y", "openssh-server"], check=True)
            elif shutil.which("apk"):
                subprocess.run(["apk", "add", "openssh"], check=True)

        # Create host keys if none exist
        os.makedirs("/etc/ssh/", exist_ok=True)
        if not os.path.exists("/etc/ssh/ssh_host_rsa_key"):
            subprocess.run(["ssh-keygen", "-A"], check=True)

        # Start sshd on free port
        port = self._find_free_port(22)
        proc = subprocess.Popen(
            ["sshd", "-p", str(port), "-o", "PubkeyAuthentication=yes", "-o", "PasswordAuthentication=no"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return f"OpenSSH started on port {port} (PID: {proc.pid})"

    def _find_free_port(self, default_port: int = 22) -> int:
        """Find a free port starting from default_port"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", default_port))
                return default_port
            except OSError:
                # Try ports up to 2222
                for p in range(2222, 2300):
                    try:
                        s.bind(("", p))
                        return p
                    except:
                        continue
        return 2222

    def status(self) -> dict:
        """Check if SSH server is running"""
        try:
            result = subprocess.run(["pgrep", "-f", "dropbear|sshd"], capture_output=True, text=True)
            if result.stdout.strip():
                return {"running": True, "pids": result.stdout.strip().splitlines()}
            return {"running": False}
        except Exception as e:
            return {"running": False, "error": str(e)}

    def start(self) -> dict:
        """Alias for install()"""
        return self.install()
