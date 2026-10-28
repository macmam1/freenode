"""
Reverse SSH Tunnel Module — Expose local SSH/services externally
"""

import subprocess
import os
import json
import time
from pathlib import Path
from typing import Optional, Dict

class ReverseTunnel:
    """Manage reverse SSH tunnels (autossh / ssh -R)"""

    def __init__(self, remote_host: str = "sshx.io", remote_port: int = 22, local_port: int = 22):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.proc = None

    def start(self, ssh_target: str, remote_forward_port: int = 2222) -> dict:
        """Start reverse SSH tunnel via autossh or ssh -R"""
        try:
            # Check if autossh is available
            cmd_tool = "autossh" if shutil.which("autossh") else "ssh"
            
            # Build command
            if cmd_tool == "autossh":
                cmd = [
                    "autossh", "-M", "0", "-o", "ServerAliveInterval=30",
                    "-o", "ServerAliveCountMax=3", "-N", "-R",
                    f"{remote_forward_port}:localhost:{self.local_port}",
                    ssh_target
                ]
            else:
                cmd = [
                    "ssh", "-o", "ServerAliveInterval=30",
                    "-o", "ServerAliveCountMax=3", "-N", "-R",
                    f"{remote_forward_port}:localhost:{self.local_port}",
                    ssh_target
                ]

            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            time.sleep(3)
            if self.proc.poll() is None:
                return {
                    "status": "running",
                    "pid": self.proc.pid,
                    "forward_port": remote_forward_port,
                    "command": " ".join(cmd),
                }
            else:
                err = self.proc.stderr.read().decode()
                return {"status": "failed", "error": err}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop(self) -> bool:
        """Stop reverse tunnel"""
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
                return True
            except:
                try:
                    self.proc.kill()
                    return True
                except:
                    pass
        return False

    def status(self) -> dict:
        """Check tunnel status"""
        if self.proc and self.proc.poll() is None:
            return {"running": True, "pid": self.proc.pid}
        return {"running": False}
