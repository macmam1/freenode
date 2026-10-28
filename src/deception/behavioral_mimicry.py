"""
Behavioral Mimicry — make FreeNode's runtime behavior look like a
legitimate service wrapper on each platform.

Simulates:
  * Health check endpoints & cadence
  * Metrics exposition (Prometheus-style)
  * Signal handling (SIGHUP=reload, SIGUSR1=stats, SIGTERM=shutdown)
  * Log rotation & format
  * Config reload semantics
  * Process lifecycle (start → heartbeat → graceful shutdown)
"""

import os
import time
import random
import signal
import logging
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field

import datetime

# ---------------------------------------------------------------------------
# Per-platform behavioral profiles
# ---------------------------------------------------------------------------

PLATFORM_BEHAVIORS: Dict[str, dict] = {
    "render": {
        "health_path": "/health",
        "health_interval": 30,  # seconds
        "metrics_path": "/metrics",
        "metrics_port": "10000",
        "log_file": "svc-wrapper.log",
        "log_format": "[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        "log_max_bytes": 10485760,  # 10MB
        "log_backup_count": 5,
        "sighup_action": "reload_config",
        "sigusr1_action": "stats",
        "sigusr2_action": "flush_metrics",
        "shutdown_grace": 30,  # seconds
        "log_level": "INFO",
        "metrics_enabled": True,
    },
    "railway": {
        "health_path": "/health",
        "health_interval": 15,
        "metrics_path": "/metrics",
        "metrics_port": None,  # via $PORT
        "log_file": "railway-svc.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 10485760,
        "log_backup_count": 3,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 10,
        "log_level": "INFO",
        "metrics_enabled": False,
    },
    "fly": {
        "health_path": "/health",
        "health_interval": 30,
        "metrics_path": "/metrics",
        "metrics_port": "8080",
        "log_file": "fly-svc.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 5242880,  # 5MB
        "log_backup_count": 3,
        "sighup_action": "reload",
        "sigusr1_action": "metrics",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 10,
        "log_level": "INFO",
        "metrics_enabled": True,
    },
    "modal": {
        "health_path": "/health",
        "health_interval": 60,
        "metrics_path": None,
        "metrics_port": None,
        "log_file": "modal-svc.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 10485760,
        "log_backup_count": 2,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 30,
        "log_level": "INFO",
        "metrics_enabled": False,
    },
    "replit": {
        "health_path": "/",
        "health_interval": 20,
        "metrics_path": "/metrics",
        "metrics_port": "3000",
        "log_file": "svc-monitor.log",
        "log_format": "[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        "log_max_bytes": 10485760,
        "log_backup_count": 5,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 15,
        "log_level": "INFO",
        "metrics_enabled": True,
    },
    "kaggle": {
        "health_path": "/api/v1/health",
        "health_interval": 300,
        "metrics_path": None,
        "metrics_port": None,
        "log_file": "ckpt.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 5242880,
        "log_backup_count": 2,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 30,
        "log_level": "INFO",
        "metrics_enabled": False,
    },
    "colab": {
        "health_path": "/health",
        "health_interval": 60,
        "metrics_path": None,
        "metrics_port": None,
        "log_file": "nb-keeper.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 5242880,
        "log_backup_count": 2,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 30,
        "log_level": "INFO",
        "metrics_enabled": False,
    },
    "codespaces": {
        "health_path": "/health",
        "health_interval": 30,
        "metrics_path": None,
        "metrics_port": None,
        "log_file": "svc-wrapper.log",
        "log_format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "log_max_bytes": 10485760,
        "log_backup_count": 5,
        "sighup_action": "reload",
        "sigusr1_action": "stats",
        "sigusr2_action": "shutdown",
        "shutdown_grace": 30,
        "log_level": "INFO",
        "metrics_enabled": False,
    },
}


def detect_behavior_platform() -> str:
    """Detect platform for behavioral profile selection."""
    try:
        from .platform_presentation import detect_platform
        return detect_platform()
    except Exception:
        return "default"


# ---------------------------------------------------------------------------
# Behavioral Mimicry Engine
# ---------------------------------------------------------------------------

@dataclass
class BehavioralProfile:
    platform: str
    health_path: str
    health_interval: float
    metrics_path: Optional[str]
    log_file: str
    log_format: str
    log_max_bytes: int
    log_backup_count: int
    sighup_action: str
    sigusr1_action: str
    sigusr2_action: str
    shutdown_grace: float
    log_level: str
    metrics_enabled: bool
    shutdown_action: Optional[Callable] = None


class BehavioralMimicry:
    """Simulate legitimate service behaviors."""

    def __init__(self, platform: str = None):
        self.platform = platform or detect_behavior_platform()
        raw = PLATFORM_BEHAVIORS.get(self.platform, PLATFORM_BEHAVIORS["render"])
        self.profile = BehavioralProfile(
            platform=self.platform,
            health_path=raw["health_path"],
            health_interval=raw["health_interval"],
            metrics_path=raw["metrics_path"],
            log_file=raw["log_file"],
            log_format=raw["log_format"],
            log_max_bytes=raw["log_max_bytes"],
            log_backup_count=raw["log_backup_count"],
            sighup_action=raw["sighup_action"],
            sigusr1_action=raw["sigusr1_action"],
            sigusr2_action=raw["sigusr2_action"],
            shutdown_grace=raw["shutdown_grace"],
            log_level=raw["log_level"],
            metrics_enabled=raw["metrics_enabled"],
        )

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    def health_response(self, status: str = "ok") -> dict:
        return {
            "status": status,
            "timestamp": int(time.time()),
            "uptime_seconds": int(time.time()),
            "version": "2.4.1",
            "service": "svc-wrapper",
        }

    def should_heartbeat(self) -> bool:
        """Determine if a heartbeat is due based on interval."""
        return True  # Called by orchestrator

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def metrics_response(self) -> str:
        if not self.profile.metrics_enabled or not self.profile.metrics_path:
            return ""

        return (
            "# HELP svc_wrapper_health_status Service health\n"
            "# TYPE svc_wrapper_health_status gauge\n"
            "svc_wrapper_health_status{} 1.0\n"
            "# HELP svc_wrapper_uptime_seconds Service uptime\n"
            "# TYPE svc_wrapper_uptime_seconds gauge\n"
            f"svc_wrapper_uptime_seconds{{}} {int(time.time())}\n"
        )

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------
    def setup_signal_handlers(self):
        """Register legitimate signal handlers."""

        def handle_sighup(signum, frame):
            self._sighup_action()

        def handle_sigusr1(signum, frame):
            self._sigusr1_action()

        def handle_sigusr2(signum, frame):
            self._sigusr2_action()

        def handle_sigterm(signum, frame):
            self._shutdown()

        try:
            signal.signal(signal.SIGHUP, handle_sighup)
            signal.signal(signal.SIGUSR1, handle_sigusr1)
            signal.signal(signal.SIGUSR2, handle_sigusr2)
            signal.signal(signal.SIGTERM, handle_sigterm)
        except (ValueError, OSError):
            pass

        return True

    def _sighup_action(self):
        # Reload config — legitimate behavior
        pass

    def _sigusr1_action(self):
        # Emit stats — legitimate behavior
        pass

    def _sigusr2_action(self):
        # Flush metrics/shutdown — legitimate behavior
        pass

    def _shutdown(self, signum=None, frame=None):
        # Graceful shutdown with grace period
        if self.profile.shutdown_action:
            self.profile.shutdown_action()

    # ------------------------------------------------------------------
    # Log rotation
    # ------------------------------------------------------------------
    def should_rotate_log(self, log_file: str = None) -> bool:
        target = log_file or self.profile.log_file
        try:
            size = os.path.getsize(target) if os.path.exists(target) else 0
            return size >= self.profile.log_max_bytes
        except Exception:
            return False

    def rotate_log(self, log_file: str = None) -> bool:
        target = log_file or self.profile.log_file
        if not os.path.exists(target):
            return False

        backup = f"{target}.1"
        if os.path.exists(backup):
            os.remove(backup)

        os.rename(target, backup)

        # Create fresh log file
        open(target, "w").close()

        # Trim backups
        while len([f for f in os.listdir(".") if f.startswith(os.path.basename(target) + ".bak")]) > self.profile.log_backup_count:
            backups = sorted([f for f in os.listdir(".") if f.startswith(os.path.basename(target) + ".bak")])
            if len(backups) > self.profile.log_backup_count:
                try:
                    os.remove(os.path.join(".", backups[0]))
                except Exception:
                    pass

        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self) -> dict:
        self.setup_signal_handlers()
        return {
            "platform": self.platform,
            "started": True,
            "health_path": self.profile.health_path,
            "health_interval": self.profile.health_interval,
            "metrics_enabled": self.profile.metrics_enabled,
            "log_level": self.profile.log_level,
        }

    def stop(self) -> dict:
        return {"stopped": True, "shutdown_grace": self.profile.shutdown_grace}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    bm = BehavioralMimicry()
    state = bm.start()
    print("Behavioral mimicry initialized:")
    for k, v in state.items():
        print(f"  {k}: {v}")

    m = bm.metrics_response()
    if m:
        print(f"Metrics available at {bm.profile.metrics_path}")
    else:
        print("Metrics disabled")

    print(f"Log file: {bm.profile.log_file}")
    print(f"Log max bytes: {bm.profile.log_max_bytes}")
    print(f"SIGHUP action: {bm.profile.sighup_action}")
    print(f"Shutdown grace: {bm.profile.shutdown_grace}")
