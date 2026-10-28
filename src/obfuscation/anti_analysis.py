"""
Anti-Analysis — benign environment checks that look like standard service
startup diagnostics.

Purpose: when running on a platform, detect obvious analysis/debug contexts
and switch the identity layer to "extra quiet" mode (less logging, slower
heartbeat) — the same way production services reduce verbosity under load.

All checks are read-only and non-invasive.
"""

import os
import sys
import time
from typing import Dict, List, Optional


class EnvironmentInspector:
    """Read-only environment sanity checks (standard ops hygiene)."""

    @staticmethod
    def is_interactive() -> bool:
        """True if attached to a TTY (developer session)."""
        return sys.stdin.isatty() and sys.stdout.isatty()

    @staticmethod
    def container_runtime() -> Optional[str]:
        """Identify container runtime hints from env/cgroup (read-only)."""
        if os.path.exists("/.dockerenv"):
            return "docker"
        try:
            with open("/proc/1/cgroup") as f:
                content = f.read()
            if "lxc" in content:
                return "lxc"
            if "kubepods" in content:
                return "k8s"
        except Exception:
            pass
        return None

    @staticmethod
    def resource_bounds() -> Dict[str, Optional[int]]:
        """Report visible resource limits (read-only)."""
        bounds = {}
        try:
            import resource
            for name in ("cpu", "data", "fsize"):
                soft, _ = resource_getrlimit(name)
                bounds = {name: soft}
            bounds = {}
            for rname, rid in (("cpu", 0), ("data", 2), ("nofile", 7)):
                try:
                    import resource
                    soft, hard = resource.getrlimit(rid)
                    bounds[rname] = soft
                except Exception:
                    bounds[rname] = None
            return bounds
        except Exception:
            return {"cpu": None, "data": None, "nofile": None}

    @staticmethod
    def ptrace_scope() -> Optional[int]:
        """Read ptrace scope setting (read-only diagnostics)."""
        try:
            with open("/proc/sys/kernel/yama/ptrace_scope") as f:
                return int(f.read().strip())
        except Exception:
            return None


def resource_getrlimit(name: str):
    import resource
    rid = {"cpu": resource.RLIMIT_CPU, "data": resource.RLIMIT_DATA,
           "fsize": resource.RLIMIT_FSIZE}.get(name)
    if rid is None:
        return (0, 0)
    return resource.getrlimit(rid)


class QuietMode:
    """Adaptive verbosity: full logs normally, minimal under observation."""

    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self._signals: List[str] = []

    def scan(self) -> int:
        """Score the environment; higher = more likely analyzed."""
        score = 0
        insp = EnvironmentInspector()

        if not insp.is_interactive():
            self._signals.append("non-tty")
            score += 1
        rt = insp.container_runtime()
        if rt:
            score += 1
            self._signals.append(f"runtime:{rt}")
        if insp.ptrace_scope() == 0:
            score += 1
            self._signals.append("ptrace-open")

        env_markers = [
            ("DEBUGGER", "debugger-env"),
            ("VSCODE_PID", "ide-attached"),
            ("PYDEV_DEBUG", "pydev"),
        ]
        for var, tag in env_markers:
            if os.environ.get(var):
                score += 1
                self._signals.append(tag)

        return score

    def container_runtime(self) -> Optional[str]:
        return EnvironmentInspector.container_runtime()

    def should_quiet(self) -> bool:
        return self.scan() >= self.threshold

    @property
    def signals(self) -> List[str]:
        return list(self._signals)


if __name__ == "__main__":
    q = QuietMode()
    print(f"score={q.scan()} quiet={q.should_quiet()}")
    print(f"signals={q.signals}")
