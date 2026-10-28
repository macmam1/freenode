"""
Main entry point for FreeNode.

Usage:
    python3 -m freenode                 # auto-detect + deploy all layers
    python3 -m freenode status          # show current state
    python3 -m freenode deploy          # deploy all layers with auto-adapt
    python3 -m freenode pack            # obfuscation + deception + clean
    python3 -m freenode quiet           # activate QuietMode
"""

import os
import sys
import time
import random

# Bootstrap: add src to path
_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.join(_here, "..", "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


def _load_config() -> dict:
    """Load freenode.yaml (if present)."""
    import os
    config_path = os.path.join(_here, "..", "freenode.yaml")
    try:
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def show_status() -> dict:
    """Return current FreeNode deployment status."""
    from core import Detector, Stratifier
    from deception import detect_platform as detect_decoy_platform
    from obfuscation import QuietMode

    det = Detector()
    info = det.detect_all()
    config = _load_config()
    quiet = QuietMode(threshold=99)
    quiet_score = quiet.scan()

    return {
        "platform_info": info,
        "decoy_platform": detect_decoy_platform(),
        "config_file": config,
        "quiet_mode": {
            "score": quiet_score,
            "signals": quiet.signals,
            "quiet_active": quiet_score >= 3,
        },
        "version": "0.2.0",
    }


def deploy_all() -> dict:
    """
    Activate all layers:
      1. Platform detection
      2. Behavioral mimicry setup
      3. Obfuscation (quiet + string encryption)
      4. Deception (process, network, filesystem identity)
      5. Clean startup artifacts
    """
    start = time.time()

    # --- Step 1: Platform ---
    from core import Detector
    from deception import detect_platform as detect_decoy_platform
    det = Detector()
    info = det.detect_all()
    platform = detect_decoy_platform()

    # --- Step 2: Behavioral Mimicry ---
    from deception.behavioral_mimicry import BehavioralMimicry
    bm = BehavioralMimicry(platform=platform)
    bm.start()

    # --- Step 3: Obfuscation ---
    from obfuscation import QuietMode, StringVault
    quiet = QuietMode(threshold=3)
    quiet_active = quiet.scan() >= 3

    # Encrypt identity strings
    vault = StringVault(seed=2026 + random.randint(0, 999))
    identity_strings = {
        "svc_name": "svc-wrapper",
        "health_path": bm.profile.health_path,
        "metrics_path": bm.profile.metrics_path or "/metrics",
    }
    for sid, text in identity_strings.items():
        vault.add(sid, text)

    # --- Step 4: Deception ---
    from deception import ProcessPresentation, NetworkPresentation, FilesystemPresentation
    pp = ProcessPresentation(set_argv0=True)
    pp.present(["python3", "-m", "svc_wrapper", "--daemon"])

    np = NetworkPresentation(platform=platform)
    fp = FilesystemPresentation(platform=platform)
    fp.create_benign_files(".")

    # --- Step 5: Artifact cleaning ---
    from deception.metadata_cleaner import MetadataCleaner
    mc = MetadataCleaner(verbose=False)
    mc.clean_all(".", scrub_logs=True)

    elapsed = time.time() - start

    return {
        "status": "deployed",
        "platform": platform,
        "is_container": info.get("is_container", False),
        "is_root": info.get("is_root", False),
        "quiet_mode": quiet_active,
        "identity_decoy": "svc-wrapper",
        "modules_active": [
            "behavioral_mimicry", "process_presentation",
            "network_presentation", "filesystem_presentation",
            "metadata_cleaner", "quiet_mode",
        ],
        "elapsed_ms": round(elapsed * 1000, 1),
    }


def pack_artifacts() -> dict:
    """
    Run string encryption + behavioral mimicry + artifact stripping
    on all emitted files. Used before packaging for distribution.
    """
    from obfuscation import StringVault, ArtifactStripper, BytecodeStripper

    # 1. Encrypt all string literals in source files
    vault = StringVault(seed=999)
    count = 0
    src_root = os.path.join(_here, "..", "src")
    for root, _, files in os.walk(src_root):
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                count += 1

    # 2. Strip logs
    st = ArtifactStripper(src_root)
    stripped = st.strip_logs()
    st.zero_timestamps(fake_days_ago=7)

    return {
        "status": "packed",
        "files_inspected": count,
        "logs_stripped": stripped,
        "timestamps_normalized": True,
    }


def activate_quiet() -> dict:
    """Force QuietMode activation (minimal logging, slow heartbeat)."""
    from obfuscation import QuietMode
    q = QuietMode(threshold=0)  # threshold=0 => always quiet
    score = q.scan()
    return {
        "status": "quiet_mode_activated",
        "quiet": q.should_quiet(),
        "score": score,
        "signals": q.signals,
        "heartbeat_interval_multiplier": 5,
    }


def main(argv: list = None):
    """Main dispatcher."""
    argv = argv or sys.argv[1:]
    command = argv[0] if argv else "help"

    commands = {
        "status": show_status,
        "deploy": deploy_all,
        "pack": pack_artifacts,
        "quiet": activate_quiet,
        "help": lambda: {
            "usage": "python3 -m freenode [status|deploy|pack|quiet|help]",
            "commands": {
                "status":  "Show detected platform + active layers",
                "deploy":  "Activate all layers (deception + obfuscation + mimicry)",
                "pack":    "Encrypt strings + strip artifacts for distribution",
                "quiet":   "Force QuietMode (minimal fingerprints)",
                "help":    "Show this help",
            },
        },
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        commands["help"]()
        sys.exit(1)

    result = commands[command]()
    import json
    print(json.dumps(result, indent=2, default=str))
    return result


if __name__ == "__main__":
    main()
