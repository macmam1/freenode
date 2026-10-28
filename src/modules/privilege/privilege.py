"""
Privilege Module — Escalate privileges / install sudoers / set capabilities
"""

import subprocess
import os
import pwd
import json
import shutil
from typing import Optional, Dict, List

class Privilege:
    """Privilege escalation and sudoers setup"""

    def __init__(self):
        self.escalated = False
        self.escalation_method = None
        self.user = self.get_current_user()
        self.user_id = os.getuid()

    def get_current_user(self) -> str:
        """Get current username"""
        try:
            return pwd.getpwuid(os.getuid()).pw_name
        except:
            return "unknown"

    def escalate(self, method: str = "sudo") -> dict:
        """Try to escalate privileges"""
        result = {"status": "pending", "method": method, "current_user": self.user, "current_uid": self.user_id}

        if method == "sudo":
            return self._sudo_escalation()
        elif method == "proot":
            return self._proot_escalation()
        elif method == "su":
            return self._su_escalation()
        elif method == "capability":
            return self._capability_escalation()
        else:
            return {"status": "error", "message": f"Unknown method: {method}"}

    def _sudo_escalation(self) -> dict:
        """Escalate via sudo"""
        result = {"status": "pending", "method": "sudo"}

        # Check if sudo is available
        if not shutil.which("sudo"):
            return {"status": "not_installed", "method": "sudo", "message": "sudo not installed"}

        # Check if passwordless sudo is configured
        try:
            with open("/etc/sudoers", "r") as f:
                content = f.read()
            if "NOPASSWD" in content:
                result["status"] = "ok"
                result["passwordless"] = True
                self.escalated = True
                self.escalation_method = "sudo"
                return result
        except:
            result["status"] = "error"
            result["message"] = "Cannot read sudoers file"

        return result

    def _proot_escalation(self) -> dict:
        """Escalate via proot (fake root)"""
        if not shutil.which("proot"):
            return {"status": "not_installed", "method": "proot", "message": "proot not installed"}

        try:
            # Test proot root access
            result = subprocess.run(
                ["proot", "-r", "/", "-0", "whoami"],
                capture_output=True, text=True
            )
            if result.stdout.strip() == "root":
                self.escalated = True
                self.escalation_method = "proot"
                return {"status": "ok", "method": "proot", "fake_root": True}
            return {"status": "failed", "method": "proot", "output": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _su_escalation(self) -> dict:
        """Escalate via su"""
        try:
            proc = subprocess.run(
                ["su", "-c", "whoami"],
                capture_output=True, text=True,
                timeout=5
            )
            if proc.returncode == 0 and proc.stdout.strip() == "root":
                self.escalated = True
                self.escalation_method = "su"
                return {"status": "ok", "method": "su"}
            return {"status": "failed", "method": "su", "output": proc.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _capability_escalation(self) -> dict:
        """Set Linux capabilities"""
        if not shutil.which("setcap"):
            return {"status": "not_installed", "method": "capability"}

        try:
            # Add capabilities to current process
            subprocess.run(["setcap", "cap_setuid=ep", "/proc/self/exe"], capture_output=True)
            return {"status": "ok", "method": "capability"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def install_sudoers(self, user: str = None, commands: List[str] = None) -> dict:
        """Install sudoers entry for user"""
        if user is None:
            user = self.user
        if commands is None:
            commands = ["ALL=(ALL) NOPASSWD:ALL"]

        try:
            sudoers_entry = f"{user} ALL=(ALL) NOPASSWD:ALL"
            with open("/etc/sudoers", "a") as f:
                f.write(f"\n# FreeNode auto-generated\n{sudoers_entry}\n")
            
            # Validate with visudo (if available)
            if shutil.which("visudo"):
                subprocess.run(["visudo", "-c"], check=True)
            
            return {"status": "ok", "user": user, "commands": commands}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def remove_sudoers(self, user: str = None) -> dict:
        """Remove sudoers entry"""
        if user is None:
            user = self.user

        try:
            # Read sudoers file
            sudoers_path = "/etc/sudoers"
            with open(sudoers_path, "r") as f:
                lines = f.readlines()

            # Remove lines with user
            new_lines = [l for l in lines if user not in l]
            with open(sudoers_path, "w") as f:
                f.writelines(new_lines)

            return {"status": "ok", "user": user}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_capabilities(self) -> dict:
        """Get current process capabilities"""
        try:
            result = subprocess.run(
                ["capsh", "--print"],
                capture_output=True, text=True
            )
            return {"status": "ok", "capabilities": result.stdout}
        except:
            return {"status": "error", "message": "capsh not available"}

    def status(self) -> dict:
        """Return escalation status"""
        return {
            "current_user": self.user,
            "current_uid": self.user_id,
            "escalated": self.escalated,
            "method": self.escalation_method,
            "is_root": self.user_id == 0,
        }
