"""
Resource Bypass Module — cgroup, RAM/CPU, disk quota bypass
"""

import subprocess
import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List

class Resource:
    """Bypass cgroup/CPU/RAM/disk limits for FreeNode"""

    def __init__(self):
        self.proot_installed = False
        self.swap_enabled = False
        self.cgroup_detected = self._detect_cgroup()

    def _detect_cgroup(self) -> bool:
        """Detect if cgroup is available"""
        return os.path.exists("/proc/self/cgroup")

    def enable(self, method: str = "proot") -> dict:
        """Enable resource bypass via specified method"""
        methods = {
            "proot": self._enable_proot,
            "cgroup": self._bypass_cgroup,
            "swap": self._add_swap,
            "memory": self.optimize_memory,
            "disk": self._bypass_disk_quota,
        }

        if method not in methods:
            return {"status": "error", "message": f"Unknown method: {method}"}

        return methods[method]()

    def _enable_proot(self) -> dict:
        """Enable fake root environment via proot"""
        actions = []

        # Check if already installed
        if shutil.which("proot"):
            self.proot_installed = True
            return {"status": "ok", "method": "proot", "already_installed": True}

        try:
            # Try package manager first
            if shutil.which("apt-get"):
                subprocess.run(["apt-get", "update"], check=True, capture_output=True)
                subprocess.run(["apt-get", "install", "-y", "proot"], check=True)
                actions.append("installed via apt-get")
            elif shutil.which("yum"):
                subprocess.run(["yum", "install", "-y", "proot"], check=True)
                actions.append("installed via yum")
            elif shutil.which("apk"):
                subprocess.run(["apk", "add", "proot"], check=True)
                actions.append("installed via apk")
            else:
                # Download static binary
                url = "https://github.com/proot-me/proot/releases/download/v5.3.0/proot-x86_64"
                subprocess.run(["curl", "-L", "-o", "/usr/local/bin/proot", url], check=True)
                subprocess.run(["chmod", "+x", "/usr/local/bin/proot"], check=True)
                actions.append("installed static binary")

            self.proot_installed = True
            return {"status": "ok", "method": "proot", "actions": actions}

        except Exception as e:
            return {"status": "error", "method": "proot", "message": str(e)}

    def start_proot_env(self, rootfs: str = "/") -> dict:
        """Start proot environment"""
        if not self.proot_installed:
            install_result = self._enable_proot()
            if install_result["status"] != "ok":
                return install_result

        try:
            # Start proot shell
            cmd = ["proot", "-r", rootfs, "-0", "-w", "/root", "/bin/bash"]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"status": "ok", "pid": proc.pid, "command": " ".join(cmd)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _bypass_cgroup(self) -> dict:
        """Attempt cgroup bypass (requires root or specific capabilities)"""
        if not self.cgroup_detected:
            return {"status": "error", "message": "cgroup not detected"}

        try:
            # Read current cgroup limits
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
                current_limit = int(f.read().strip())

            # Try to increase (requires CAP_SYS_ADMIN)
            try:
                new_limit = current_limit * 2
                with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "w") as f:
                    f.write(str(new_limit))
                return {"status": "ok", "method": "cgroup", "old_limit": current_limit, "new_limit": new_limit}
            except PermissionError:
                return {"status": "error", "message": "Permission denied (need CAP_SYS_ADMIN)"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _add_swap(self, size_gb: int = 2) -> dict:
        """Add swap file to increase available memory"""
        swapfile = Path("/swapfile")
        
        if swapfile.exists():
            return {"status": "ok", "message": "swap already exists", "swap_enabled": True}

        try:
            # Create swap file
            subprocess.run(["fallocate", "-l", f"{size_gb}G", str(swapfile)], check=True)
            subprocess.run(["chmod", "600", str(swapfile)], check=True)
            subprocess.run(["mkswap", str(swapfile)], check=True)
            subprocess.run(["swapon", str(swapfile)], check=True)
            
            # Make persistent (add to /etc/fstab)
            with open("/etc/fstab", "a") as f:
                f.write("/swapfile none swap sw 0 0\n")
            
            self.swap_enabled = True
            return {"status": "ok", "method": "swap", "size_gb": size_gb}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _bypass_disk_quota(self) -> dict:
        """Bypass disk quota (platform-specific)"""
        # Check quota status
        try:
            result = subprocess.run(["quota", "-v"], capture_output=True, text=True)
            if result.returncode == 0:
                return {"status": "ok", "quota_detected": True, "output": result.stdout}
            return {"status": "ok", "quota_detected": False}
        except FileNotFoundError:
            return {"status": "ok", "quota_detected": False, "message": "quota command not found"}

    def optimize_memory(self) -> dict:
        """Optimize memory usage"""
        actions = []
        
        try:
            # Clear page cache (requires root)
            subprocess.run(["sync"], check=True)
            with open("/proc/sys/vm/drop_caches", "w") as f:
                f.write("3")
            actions.append("cleared page cache")
        except:
            actions.append("page cache clear failed (need root)")

        try:
            # Clear swap
            subprocess.run(["swapoff", "-a"], check=True)
            subprocess.run(["swapon", "-a"], check=True)
            actions.append("swap cleared")
        except:
            actions.append("swap clear failed")

        return {"status": "ok", "method": "memory_optimize", "actions": actions}

    def get_resource_status(self) -> dict:
        """Get current resource usage and limits"""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "swap_enabled": self.swap_enabled,
            "proot_installed": self.proot_installed,
            "cgroup_detected": self.cgroup_detected,
        }
