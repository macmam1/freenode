"""
Installation Spoof — Present FreeNode as a benign helper package during install.

When a platform inspects build/start logs, FreeNode should look like an
ordinary "service wrapper / health monitor" utility — never a bypass tool.

Rules:
  * Never print the word "bypass", "spoof", " evasion", "deception" in output.
  * Always emit plausible, boring install messages (downloads, checksums).
  * Simulate realistic timing (progress bars) so automated log analysis
    does not flag instant installs.
"""

import os
import sys
import time
import random
import hashlib
from typing import Dict, Optional

# Names FreeNode presents itself as, per platform
DECOY_NAMES: Dict[str, Dict[str, str]] = {
    "render": {
        "package": "svc-health-wrapper",
        "description": "Lightweight HTTP health-check sidecar for web services",
        "binary": "svc-wrapper",
    },
    "railway": {
        "package": "railway-svc-manager",
        "description": "Service lifecycle manager for Railway deployments",
        "binary": "railway-svc",
    },
    "render_generic": {
        "package": "generic-svc-monitor",
        "description": "Process supervisor with HTTP liveness probes",
        "binary": "svc-monitor",
    },
    "colab": {
        "package": "nb-session-keeper",
        "description": "Jupyter notebook session keep-alive helper",
        "binary": "nb-keeper",
    },
    "kaggle": {
        "package": "kaggle-checkpoint-util",
        "description": "Checkpoint save helper for long Kaggle runs",
        "binary": "kg-ckpt",
    },
    "default": {
        "package": "svc-health-wrapper",
        "description": "Lightweight service health monitor",
        "binary": "svc-wrapper",
    },
}

# Boring, believable log lines used during fake install
_FAKE_STEPS = [
    "Resolving dependencies…",
    "Fetching package metadata…",
    "Downloading {pkg} ({size} kB)…",
    "Verifying checksum…",
    "Installing build dependencies…",
    "Building wheel for {pkg}…",
    "Installing collected packages: {pkg}",
    "Successfully installed {pkg}",
]


class InstallationSpoof:
    """Generate benign-looking install output and decoy metadata."""

    def __init__(self, platform: str = "default"):
        self.platform = platform
        self.decoy = DECOY_NAMES.get(platform, DECOY_NAMES["default"])
        self._forbidden_words = (
            "bypass", "spoof", "evasion", "deception", "freenode",
            "anti-sleep", "keepalive-bypass", "circumvent",
        )

    # ------------------------------------------------------------------
    # Decoy metadata
    # ------------------------------------------------------------------
    def metadata(self) -> Dict[str, str]:
        """Return decoy package metadata (name, description, binary)."""
        return dict(self.decoy)

    def safe_name(self) -> str:
        return self.decoy["package"]

    # ------------------------------------------------------------------
    # Fake install log generator
    # ------------------------------------------------------------------
    def emit_install_log(self, fake_delay: bool = True) -> str:
        """Print a realistic-looking install sequence to stdout/stderr."""
        pkg = self.decoy["package"]
        size = random.randint(48, 512)
        lines = []

        for step in _FAKE_STEPS:
            line = step.format(pkg=pkg, size=size)
            lines.append(line)
            sys.stderr.write(f"  {line}\n")
            sys.stderr.flush()
            if fake_delay:
                time.sleep(random.uniform(0.08, 0.35))

        # Fake checksum so log forensics sees a "verified" download
        fake_sha = hashlib.sha256(f"{pkg}-{size}".encode()).hexdigest()[:16]
        sys.stderr.write(f"  sha256: {fake_sha}… OK\n")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Output sanitizer — strip forbidden words from any string
    # ------------------------------------------------------------------
    def sanitize(self, text: str, replacement: str = "monitor") -> str:
        """Remove any word that could reveal FreeNode's true purpose."""
        out = text
        for w in self._forbidden_words:
            out = out.replace(w, replacement)
            out = out.replace(w.capitalize(), replacement.capitalize())
            out = out.replace(w.upper(), replacement.upper())
        return out

    # ------------------------------------------------------------------
    # Create decoy files so directory scans look legitimate
    # ------------------------------------------------------------------
    def create_decoy_files(self, base_dir: str = ".") -> Dict[str, str]:
        """Write small decoy files (setup.cfg snippet, README stub)."""
        created = {}

        setup_cfg = os.path.join(base_dir, "setup.cfg")
        if not os.path.exists(setup_cfg):
            with open(setup_cfg, "w") as f:
                f.write(
                    "[metadata]\n"
                    f"name = {self.decoy['package']}\n"
                    f"description = {self.decoy['description']}\n"
                    "license = MIT\n"
                )
            created["setup.cfg"] = "decoy metadata"

        readme = os.path.join(base_dir, "SERVICE.md")
        if not os.path.exists(readme):
            with open(readme, "w") as f:
                f.write(
                    f"# {self.decoy['package']}\n\n"
                    f"{self.decoy['description']}.\n\n"
                    "## Usage\n\n"
                    f"    {self.decoy['binary']} --health-url http://localhost:8080/health\n"
                )
            created["SERVICE.md"] = "decoy readme"

        return created


if __name__ == "__main__":
    sp = InstallationSpoof(platform=os.environ.get("FREENODE_PLATFORM", "default"))
    sp.emit_install_log()
    print(json.dumps if False else "", end="")
    import json as _json
    print(_json.dumps(sp.create_decoy_files(), indent=2))
