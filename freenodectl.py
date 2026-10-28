"""
freenodectl — Command-line control plane for FreeNode.

A standalone CLI (no external dependencies) for controlling all layers:
  * Layer activation/deactivation per platform
  * Status introspection
  * Artifact packing (obfuscation + deception)
  * Quiet mode toggle
  * Config management

Usage:
    freenodectl status
    freenodectl enable ssh --platform render
    freenodectl disable tunnel
    freenodectl pack
    freenodectl quiet --on|--off
    freenodectl config --set platform=kaggle
"""

import os
import sys
import json
import argparse
import textwrap
from pathlib import Path

# Ensure we can import src/
_here = Path(__file__).resolve().parent
_src = _here / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

CONFIG_PATH = _here / "freenode.yaml"


def load_config() -> dict:
    """Load config from freenode.yaml, return defaults if missing."""
    defaults = {
        "platform": "auto",
        "modules": {
            "ssh": "disabled",
            "tunnel": "disabled",
            "keepalive": "disabled",
            "api": "disabled",
            "terminal": "disabled",
        },
        "deception": {
            "log_scrub": True,
            "behavioral_mimicry": True,
            "string_encryption": True,
        },
        "obfuscation": {
            "quiet_mode": False,
            "artifact_strip": True,
        },
    }
    if CONFIG_PATH.exists():
        try:
            import yaml
            with open(CONFIG_PATH) as f:
                loaded = yaml.safe_load(f) or {}
            _deep_merge(defaults, loaded)
        except Exception:
            pass
    return defaults


def _deep_merge(a: dict, b: dict):
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            _deep_merge(a[k], v)
        else:
            a[k] = v


def save_config(config: dict):
    """Write config back to freenode.yaml."""
    try:
        import yaml
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except ImportError:
        # Fallback: write YAML manually
        _write_yaml_manual(CONFIG_PATH, config)
        return True


def _write_yaml_manual(path: Path, data: dict, indent: int = 0):
    """Minimal YAML writer (no deps)."""
    lines = []
    _flatten_yaml(data, lines, indent)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def _flatten_yaml(data: dict | list | str, lines: list, indent: int):
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                _flatten_yaml(v, lines, indent + 1)
            else:
                val = str(v)
                if val.lower() in ("true", "false", "null") or val.isdigit():
                    lines.append(f"{pad}{k}: {val}")
                else:
                    lines.append(f'{pad}{k}: "{val}"')
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{pad}-")
                _flatten_yaml(item, lines, indent + 1)
            else:
                lines.append(f"{pad}- {item}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

class CLI:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.config = load_config()

    # --- status ---
    def cmd_status(self) -> dict:
        from core import Detector
        from deception import detect_platform as detect_decoy
        from obfuscation import QuietMode

        det = Detector()
        info = det.detect_all()
        quiet = QuietMode(threshold=99)
        score = quiet.scan()

        return {
            "version": VERSION,
            "platform_info": {
                "os": info.get("os"),
                "is_container": info.get("is_container"),
                "is_root": info.get("is_root"),
                "public_ip": info.get("public_ip"),
            },
            "decoy_platform": detect_decoy(),
            "modules_active": self.config.get("modules", {}),
            "deception": self.config.get("deception", {}),
            "quiet_mode": {
                "active": score >= 3,
                "score": score,
                "signals": quiet.signals,
            },
            "config_file": str(CONFIG_PATH) if CONFIG_PATH.exists() else None,
        }

    # --- enable ---
    def cmd_enable(self) -> dict:
        module = self.args.module
        platform = self.args.platform or self.config.get("platform", "auto")

        if platform == "auto":
            from core.detector import detect_platform
            platform = detect_platform()

        modules = self.config.setdefault("modules", {})
        old_state = modules.get(module, "disabled")
        modules[module] = "enabled"

        save_config(self.config)

        return {
            "action": "enable",
            "module": module,
            "platform": platform,
            "old_state": old_state,
            "new_state": "enabled",
        }

    # --- disable ---
    def cmd_disable(self) -> dict:
        module = self.args.module
        modules = self.config.setdefault("modules", {})
        old_state = modules.get(module, "disabled")
        modules[module] = "disabled"
        save_config(self.config)

        return {
            "action": "disable",
            "module": module,
            "old_state": old_state,
            "new_state": "disabled",
        }

    # --- pack ---
    def cmd_pack(self) -> dict:
        from obfuscation import ArtifactStripper, StringVault
        from deception.metadata_cleaner import MetadataCleaner

        # 1. Encrypt strings
        vault = StringVault(seed=2026)
        # Simulate: in real use, would scan source files
        vault.add("svc_name", "svc-wrapper")
        vault.add("health_path", "/health")

        # 2. Strip artifacts
        src_root = _here / "src"
        st = ArtifactStripper(str(src_root))
        stripped = st.strip_logs()
        st.zero_timestamps(fake_days_ago=7)

        # 3. Clean metadata
        mc = MetadataCleaner(verbose=False)
        mc.clean_all(".", scrub_logs=True)

        return {
            "action": "pack",
            "string_encryption": "done",
            "logs_stripped": stripped,
            "timestamps_normalized": True,
            "metadata_cleaned": True,
        }

    # --- quiet ---
    def cmd_quiet(self) -> dict:
        if getattr(self.args, "on", False):
            quiet = True
            self.config.setdefault("obfuscation", {})["quiet_mode"] = True
        elif getattr(self.args, "off", False):
            quiet = False
            self.config.setdefault("obfuscation", {})["quiet_mode"] = False
        else:
            quiet = not self.config.get("obfuscation", {}).get("quiet_mode", False)
            self.config.setdefault("obfuscation", {})["quiet_mode"] = quiet

        save_config(self.config)
        return {"quiet_mode": quiet, "status": "updated"}

    # --- config ---
    def cmd_config(self) -> dict:
        if self.args.set:
            key, _, val = self.args.set.partition("=")
            keys = key.split(".")
            d = self.config
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = val
            save_config(self.config)
            return {"action": "set", "key": key, "value": val}
        else:
            return self.config


def get_version() -> str:
    """Read version from src/version.py without importing everything."""
    vfile = _here / "src" / "version.py"
    if vfile.exists():
        with open(vfile) as f:
            for line in f:
                if line.startswith("VERSION"):
                    return line.split('"')[1]
    return "unknown"


VERSION = get_version()


# ---------------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freenodectl",
        description="FreeNode control plane",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              freenodectl status
              freenodectl enable ssh --platform render
              freenodectl disable tunnel
              freenodectl pack
              freenodectl quiet --on
              freenodectl config --set platform=kaggle
        """),
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    p_status = sub.add_parser("status", help="Show FreeNode deployment status")

    p_enable = sub.add_parser("enable", help="Enable a module")
    p_enable.add_argument("module", help="Module name (e.g. ssh, tunnel, keepalive)")
    p_enable.add_argument("--platform", "-p", help="Override platform")

    p_disable = sub.add_parser("disable", help="Disable a module")
    p_disable.add_argument("module", help="Module name")

    p_pack = sub.add_parser("pack", help="Pack artifacts (encrypt + strip)")

    p_quiet = sub.add_parser("quiet", help="Toggle QuietMode")
    qgroup = p_quiet.add_mutually_exclusive_group()
    qgroup.add_argument("--on", action="store_true", help="Enable QuietMode")
    qgroup.add_argument("--off", action="store_true", help="Disable QuietMode")

    p_config = sub.add_parser("config", help="View or modify config")
    p_config.add_argument("--set", "-s", help="Set key=value (dotted path)")

    return parser


def main(argv: list = None) -> dict:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return {}

    cli = CLI(args)
    handlers = {
        "status": cli.cmd_status,
        "enable": cli.cmd_enable,
        "disable": cli.cmd_disable,
        "pack": cli.cmd_pack,
        "quiet": cli.cmd_quiet,
        "config": cli.cmd_config,
    }

    result = handlers[args.command]()
    print(json.dumps(result, indent=2, default=str))
    return result


if __name__ == "__main__":
    main()
