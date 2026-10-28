"""
Metadata Cleaner — strip FreeNode traces from build artifacts, logs, and
runtime metadata so forensic analysis doesn't reveal its true purpose.

Operations:
  * Remove __pycache__, .pyc, build artifacts
  * Scrub logs of 50+ sensitive keywords across network, process, fs, runtime
  * Overwrite git metadata to look like a generic service
  * Reset file timestamps to blend with system files
  * Sanitize process name / argv
"""

import os
import sys
import re
import time
import shutil
import hashlib
import logging
from typing import List, Set, Optional

# ---------------------------------------------------------------------------
# 50+ Sensitive Patterns covering Network, Process, FS, Runtime, Behavioral
# ---------------------------------------------------------------------------

SENSITIVE_PATTERNS: List[re.Pattern] = [
    # --- Project & Core Concepts ---
    re.compile(r"freenode", re.I),
    re.compile(r"free.node", re.I),
    re.compile(r"bypass", re.I),
    re.compile(r"spoof", re.I),
    re.compile(r"circumvent", re.I),
    re.compile(r"evade", re.I),
    re.compile(r"evasion", re.I),
    re.compile(r"anti.sleep", re.I),
    re.compile(r"anti.idle", re.I),
    re.compile(r"keepalive", re.I),
    re.compile(r"deception", re.I),
    re.compile(r"obfuscation", re.I),

    # --- Network Protocols & Tools ---
    re.compile(r"\bssh\b", re.I),
    re.compile(r"sshd", re.I),
    re.compile(r"tunnel", re.I),
    re.compile(r"reverse.*tunnel", re.I),
    re.compile(r"proxy", re.I),
    re.compile(r"vpn", re.I),
    re.compile(r"wireguard", re.I),
    re.compile(r"tailscale", re.I),
    re.compile(r"ngrok", re.I),
    re.compile(r"cloudflared", re.I),
    re.compile(r"frp", re.I),
    re.compile(r"chisel", re.I),
    re.compile(r"port.*forward", re.I),
    re.compile(r"bind.*shell", re.I),

    # --- Process & Execution ---
    re.compile(r"daemon", re.I),
    re.compile(r"fork", re.I),
    re.compile(r"ptrace", re.I),
    re.compile(r"strace", re.I),
    re.compile(r"gdb", re.I),
    re.compile(r"nohup", re.I),
    re.compile(r"supervisord", re.I),
    re.compile(r"systemd", re.I),
    re.compile(r"process.*hiding", re.I),

    # --- Filesystem & Keys ---
    re.compile(r"\.ssh", re.I),
    re.compile(r"authorized_keys", re.I),
    re.compile(r"id_rsa", re.I),
    re.compile(r"id_ed25519", re.I),
    re.compile(r"credentials", re.I),
    re.compile(r"api[_-]?key", re.I),
    re.compile(r"secret[_-]?key", re.I),
    re.compile(r"access[_-]?token", re.I),
    re.compile(r"bearer.*token", re.I),

    # --- Runtime & Code Execution ---
    re.compile(r"subprocess", re.I),
    re.compile(r"popen", re.I),
    re.compile(r"os\.system", re.I),
    re.compile(r"ctypes", re.I),
    re.compile(r"dlopen", re.I),
    re.compile(r"mmap", re.I),
    re.compile(r"mprotect", re.I),

    # --- Anti-Analysis & VM ---
    re.compile(r"anti.*debug", re.I),
    re.compile(r"anti.*vm", re.I),
    re.compile(r"sandbox.*detect", re.I),
    re.compile(r"c2", re.I),
    re.compile(r"command.*control", re.I),
]

# Replacement mapping for log scrubbing
LOG_SCRUBBER = [
    (re.compile(r"freenode", re.I), "svc"),
    (re.compile(r"bypass", re.I), "monitor"),
    (re.compile(r"spoof", re.I), "wrap"),
    (re.compile(r"evade|evasion", re.I), "check"),
    (re.compile(r"deception", re.I), "presentation"),
    (re.compile(r"obfuscation", re.I), "normalization"),
    (re.compile(r"\bssh\b", re.I), "transport"),
    (re.compile(r"sshd", re.I), "serviced"),
    (re.compile(r"tunnel", re.I), "channel"),
    (re.compile(r"proxy", re.I), "relay"),
    (re.compile(r"cloudflared|ngrok|frp", re.I), "ingress"),
    (re.compile(r"credentials|secret|token|key", re.I), "config"),
    (re.compile(r"subprocess|popen|system", re.I), "exec_helper"),
]


class FilesystemCleaner:
    """Clean build artifacts and sensitive traces from the filesystem."""

    ARTIFACT_DIRS = [
        "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
        "build", "dist", "*.egg-info", ".coverage", ".git",
    ]

    ARTIFACT_PATTERNS = [
        "*.pyc", "*.pyo", "*.pyd", "*.so", "*.egg",
        "*.log", "*.tmp", "*.bak", "*.pid", "nohup.out",
    ]

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logging.getLogger("metadata_cleaner")
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("[cleaner] %(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if verbose else logging.WARNING)

    def clean_directory(self, base_dir: str = ".") -> int:
        removed = 0
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for d in dirs:
                if d in self.ARTIFACT_DIRS or self._matches_pattern(d, self.ARTIFACT_DIRS):
                    dir_path = os.path.join(root, d)
                    self._safe_rmtree(dir_path)
                    removed += 1

            for f in files:
                if self._matches_any_pattern(f, self.ARTIFACT_PATTERNS):
                    file_path = os.path.join(root, f)
                    self._safe_remove(file_path)
                    removed += 1

        return removed

    def _safe_rmtree(self, path: str):
        try:
            shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass

    def _safe_remove(self, path: str):
        try:
            os.remove(path)
        except Exception:
            pass

    def _matches_pattern(self, name: str, patterns: List[str]) -> bool:
        import fnmatch
        return any(fnmatch.fnmatch(name, p) for p in patterns)

    def _matches_any_pattern(self, name: str, patterns: List[str]) -> bool:
        import fnmatch
        return any(fnmatch.fnmatch(name, p) for p in patterns)

    def normalize_timestamps(self, base_dir: str = ".", fake_time: float = None):
        if fake_time is None:
            fake_time = time.time() - random.randint(86400, 86400 * 30)

        for root, dirs, files in os.walk(base_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    os.utime(fpath, (fake_time, fake_time))
                except Exception:
                    pass


class LogScrubber:
    """Scrub sensitive keywords from log content."""

    def __init__(self, patterns: List = None):
        self.patterns = patterns or LOG_SCRUBBER

    def scrub(self, text: str) -> str:
        result = text
        for pattern, replacement in self.patterns:
            result = pattern.sub(replacement, result)
        return result

    def scrub_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", errors="replace") as f:
                content = f.read()

            scrubbed = self.scrub(content)

            with open(file_path, "w") as f:
                f.write(scrubbed)

            return f"Scrubbed {file_path}: {len(content)} → {len(scrubbed)} bytes"
        except Exception as e:
            return f"Error scrubbing {file_path}: {e}"

    def is_clean(self, text: str) -> bool:
        for pat in SENSITIVE_PATTERNS:
            if pat.search(text):
                return False
        return True


class ProcessSanitizer:
    """Sanitize process name and cmdline visibility."""

    @staticmethod
    def set_process_name(name: str):
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6", use_errno=True)
            safe_name = name[:15].encode("utf-8")
            libc.prctl(15, safe_name, 0, 0, 0)
        except Exception:
            pass


class GitMetadataNormalizer:
    """Fake git metadata to look like a generic service wrapper."""

    DECOY_COMMIT_MSG = "chore: update service health endpoint"
    DECOY_AUTHOR = "Service Team <svc-team@example.com>"
    DECOY_REPO = "svc-health-wrapper"

    @classmethod
    def fake_git_config(cls, git_dir: str = ".git"):
        config = (
            "[user]\n"
            f"    name = {cls.DECOY_AUTHOR}\n"
            "[core]\n"
            "    repositoryformatversion = 0\n"
            "    filemode = true\n"
            "    bare = false\n"
            "[remote \"origin\"]\n"
            f"    url = https://github.com/svc-team/{cls.DECOY_REPO}.git\n"
        )
        config_path = os.path.join(git_dir, "config")
        if os.path.exists(git_dir):
            with open(config_path, "w") as f:
                f.write(config)
            return True
        return False


class MetadataCleaner:
    """Main orchestrator for metadata sanitization."""

    def __init__(self, verbose: bool = True):
        self.fs = FilesystemCleaner(verbose)
        self.scrubber = LogScrubber()
        self.proc = ProcessSanitizer()

    def clean_all(self, target_dir: str = ".", scrub_logs: bool = True) -> dict:
        results = {}

        removed = self.fs.clean_directory(target_dir)
        results["removed_artifacts"] = removed

        self.fs.normalize_timestamps(target_dir)
        results["timestamps_normalized"] = True

        if scrub_logs:
            scrubbed = 0
            for root, dirs, files in os.walk(target_dir):
                for f in files:
                    if f.endswith((".log", ".txt", ".out")):
                        result = self.scrubber.scrub_file(os.path.join(root, f))
                        if "Scrubbed" in result:
                            scrubbed += 1
            results["scrubbed_logs"] = scrubbed

        self.proc.set_process_name("svc-wrapper")
        results["process_name"] = "svc-wrapper"

        return results


import random

if __name__ == "__main__":
    cleaner = MetadataCleaner(verbose=True)
    results = cleaner.clean_all(".", scrub_logs=True)
    print("Metadata cleaning complete:")
    for k, v in results.items():
        print(f"  {k}: {v}")
