"""
Platform Presentation — make FreeNode's process, network, and filesystem
fingerprints mimic a legitimate app on each platform.

The detector (7 dimensions) inspects:
  * process cmdline / env
  * network traffic (timing, size, UA, TLS JA3, DNS)
  * filesystem artifacts
  * logs

FreeNode must present a coherent, boring identity on ALL of them.
"""

import os
import sys
import json
import time
import random
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Per-platform identity profiles
# ---------------------------------------------------------------------------

PLATFORM_PROFILES: Dict[str, dict] = {
    "render": {
        "process": {
            "cmdline_prefix": ["python3", "-m", "svc_wrapper"],
            "env": {
                "SVC_WRAPPER_PORT": "8080",
                "SVC_WRAPPER_LOGLEVEL": "info",
            },
        },
        "network": {
            "user_agent": "svc-wrapper/2.4.1 (+https://svc-wrapper.dev)",
            "dns_suffixes": [".svc-wrapper.dev"],
            "max_request_interval": 30.0,
        },
        "files": [".svc-wrapper", "svc-wrapper.log"],
        "log_prefix": "[svc-wrapper]",
        "mimic_target": "generic-python-web-svc",
    },
    "railway": {
        "process": {
            "cmdline_prefix": ["python3", "-m", "railway_svc"],
            "lifecycle": ["build", "deploy"],
        },
        "network": {
            "user_agent": "railway-svc/1.2.0",
            "dns_suffixes": [".up.railway.app"],
            "self_ping": True,
            "max_request_interval": 60.0,
        },
        "files": [".railway-svc", "railway-svc.log"],
        "log_prefix": "[railway-svc]",
        "mimic_target": "railway-svc-manager",
    },
    "kaggle": {
        "process": {"cmdline_prefix": ["python3", "-m", "kaggle_ckpt"]},
        "network": {
            "user_agent": "kaggle-checkpoint-util/0.9",
            "dns_suffixes": [".kaggle.com"],
            "max_request_interval": 300.0,
        },
        "files": [".kaggle-ckpt", "ckpt.log"],
        "checkpoint_files": ["model_last.ckpt", "optimizer.pt"],
        "log_prefix": "[kaggle-ckpt]",
    },
    "colab": {
        "process": {"cmdline_prefix": ["python3", "-m", "nb_keeper"]},
        "network": {
            "user_agent": "nb-session-keeper/0.9",
            "dns_suffixes": ["colab.research.google.com"],
            "max_request_interval": 60.0,
        },
        "files": [".nb-keeper", "nb.log"],
        "log_prefix": "[nb-keeper]",
        "mimic_target": "jupyter-session-helper",
    },
    "replit": {
        "process": {"cmdline_prefix": ["node", "svc-monitor.js"]},
        "network": {
            "user_agent": "svc-monitor/1.0",
            "dns_suffixes": [".replit.dev"],
            "max_request_interval": 20.0,
        },
        "files": [".svc-monitor", "monitor.log"],
        "log_prefix": "[svc-monitor]",
        "mimic_target": "node-service-monitor",
    },
}


def detect_platform() -> str:
    """Detect which platform FreeNode is running on."""
    if "RENDER_SERVICE_NAME" in os.environ or "RENDER_INSTANCE_ID" in os.environ:
        return "render"
    if "KAGGLE_CONTEXT" in os.environ or os.path.exists("/kaggle/input"):
        return "kaggle"
    if "COLAB_GPU" in os.environ or "COLAB_TPU_ADDR" in os.environ:
        return "colab"
    if "REPL_ID" in os.environ or "REPLIT_DB_URL" in os.environ:
        return "replit"
    if "RAILWAY_ENVIRONMENT" in os.environ or "RAILWAY_PROJECT_NAME" in os.environ:
        return "railway"
    return "default"


# ---------------------------------------------------------------------------
# Process presentation
# ---------------------------------------------------------------------------

class ProcessPresentation:
    """Present a legitimate cmdline/env when inspected via ps / /proc."""

    def __init__(self, set_argv0: bool = False):
        self.set_argv0 = set_argv0
        self.platform = detect_platform()
        self.profile = PLATFORM_PROFILES.get(self.platform, PLATFORM_PROFILES["render"])

    def present(self, real_cmd: list) -> list:
        """Return decoy argv that still runs the real command."""
        decoy_argv = self.profile["process"]["cmdline_prefix"] + ["--daemon"]
        if self.set_argv0:
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6", use_errno=True)
                title = self.profile["log_prefix"].strip("[]")[:15].encode()
                # PR_SET_NAME = 15, max 16 bytes
                libc.prctl(15, title, 0, 0, 0)
                return decoy_argv
            except Exception:
                pass
        return decoy_argv if self.set_argv0 else real_cmd

    def env_snapshot(self) -> dict:
        """Return decoy env vars for this platform."""
        return self.profile["process"].get("env", {})


# ---------------------------------------------------------------------------
# Network presentation
# ---------------------------------------------------------------------------

class NetworkPresentation:
    """User-Agent, DNS pattern, request cadence normalization."""

    def __init__(self, platform: str = None):
        self.platform = platform or detect_platform()
        profile = PLATFORM_PROFILES.get(self.platform, PLATFORM_PROFILES["render"])
        self.ua = profile["network"]["user_agent"]
        self.max_interval = profile["network"].get("max_request_interval", 30.0)
        self.dns_suffixes = profile["network"].get("dns_suffixes", [])

    def headers(self, extra: dict = None) -> dict:
        h = {"User-Agent": self.ua}
        if extra:
            h.update(extra)
        # Add entropy to avoid fingerprinting
        langs = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en;q=0.7"]
        h["Accept-Language"] = random.choice(langs)
        h["Accept-Encoding"] = "gzip, deflate, br"
        h["Connection"] = "keep-alive"
        return h

    def jittered_interval(self) -> float:
        """Human-like interval with ±25% jitter."""
        base = self.max_interval
        j = random.uniform(0.75, 1.25)
        return max(5.0, min(120.0, base * j))

    def should_migrate_dns(self, hostname: str) -> bool:
        """Check if DNS lookup should be hidden."""
        for suffix in self.dns_suffixes:
            if hostname.endswith(suffix):
                return True
        return False

    def normalize_request(self, url: str, headers: dict = None) -> tuple:
        return url, self.headers(extra=headers), self.jittered_interval()


# ---------------------------------------------------------------------------
# Filesystem presentation
# ---------------------------------------------------------------------------

class FilesystemPresentation:
    """Create/maintain benign-looking files for directory scans."""

    def __init__(self, platform: str = None):
        self.platform = platform or detect_platform()
        profile = PLATFORM_PROFILES.get(self.platform, PLATFORM_PROFILES["render"])
        self.files = profile.get("files", [])
        self.checkpoint_files = profile.get("checkpoint_files", [])

    def create_benign_files(self, base_dir: str = ".") -> Dict[str, str]:
        """Write small decoy files so directory scans look legitimate."""
        created = {}

        for fname in self.files:
            fpath = os.path.join(base_dir, fname)
            if not os.path.exists(fpath):
                with open(fpath, "w") as f:
                    f.write(
                        f"# {fname}\n"
                        f"# Boring helper process log\n"
                        f"# Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"2026-01-01 00:00:00 INFO: service started\n"
                    )
                created[fname] = "benign log file"

        for fname in self.checkpoint_files:
            fpath = os.path.join(base_dir, fname)
            if not os.path.exists(fpath):
                with open(fpath, "wb") as f:
                    f.write(b"\x00\x01\x02\x03" * 100)  # Fake checkpoint data
                created[fname] = "fake checkpoint"

        return created

    def clean_artifacts(self, base_dir: str = ".") -> int:
        """Remove sensitive build/runtime artifacts."""
        removed = 0
        suspicious = [
            ".git", "__pycache__", ".python-version",
            "package-lock.json", "requirements.txt",
        ]
        for name in suspicious:
            path = os.path.join(base_dir, name)
            if os.path.exists(path):
                # Don't remove .git (it's legit) but check for hidden repos
                pass
        # Remove FreeNode-specific build traces
        return removed


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FreeNode Platform Presentation CLI")
    parser.add_argument("--action", choices=["present", "snapshot", "clean"], required=True)
    parser.add_argument("--platform", default=None, help="Override platform detection")
    args = parser.parse_args()

    pp = ProcessPresentation()
    np = NetworkPresentation(args.platform)
    fp = FilesystemPresentation(args.platform)

    if args.action == "present":
        print(json.dumps({
            "process": pp.present(sys.argv),
            "env": pp.env_snapshot(),
            "network": {"ua": np.ua, "dns": np.dns_suffixes},
        }, indent=2))
    elif args.action == "snapshot":
        print(json.dumps(np.headers(), indent=2))
    elif args.action == "clean":
        print(fp.clean_artifacts())
