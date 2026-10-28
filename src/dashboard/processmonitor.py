"""
Process Monitor for FreeNode Dashboard.

Provides system process information:
  - List running processes (with CPU/Memory)
  - Process details (PID, user, command, status)
  - Kill/Pause/Resume processes
  - System resource usage
"""

import os
import psutil
from typing import List, Dict, Optional


class ProcessMonitor:
    """Monitor and manage system processes."""

    @staticmethod
    def list_processes() -> List[Dict]:
        """Get list of running processes with resource info."""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'memory_percent', 'cpu_percent'])
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "user": pinfo['username'] or 'system',
                        "memory_percent": round(pinfo['memory_percent'], 2),
                        "cpu_percent": round(pinfo['cpu_percent'], 2),
                        "status": proc.status(),
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            return [{"error": str(e)}]

        # Sort by memory usage descending
        return sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=True)[:50]

    @staticmethod
    def get_process_info(pid: int) -> Dict:
        """Get detailed info for a specific process."""
        try:
            proc = psutil.Process(pid)
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status(),
                "user": proc.username(),
                "memory_info": proc.memory_info()._asdict(),
                "cpu_percent": proc.cpu_percent(),
                "num_threads": proc.num_threads(),
                "create_time": proc.create_time(),
                "cwd": proc.cwd(),
                "cmdline": " ".join(proc.cmdline()) if proc.cmdline() else "",
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def kill_process(pid: int) -> Dict:
        """Kill a process."""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return {"status": "terminated", "pid": pid}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_system_stats() -> Dict:
        """Get overall system resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent,
            },
            "processes_count": len(psutil.pids()),
        }
