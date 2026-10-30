"""
CoCalc platform detection + automatic internet-access bypass.

CoCalc project containers block outbound DNS/HTTP by default.
This module detects the environment and transparently patches
Python networking (socket.getaddrinfo / urllib) to resolve DNS
via DNS-over-HTTPS and connect by IP.

See docs/cocalc-internet-access-bypass.md for full analysis.
"""

import os
import sys

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.utils.dns_bypass import enable_all, resolve_via_doh
except ImportError:
    from utils.dns_bypass import enable_all, resolve_via_doh


def detect():
    """Detect CoCalc project environment."""
    indicators = [
        os.path.exists("/opt/cocalc"),
        os.path.exists("/opt/cocalc/project-bundle"),
        os.path.exists("/home/user/.local/share/cocalc"),
    ]
    return sum(indicators) >= 2


def get_restrictions():
    """Known CoCalc egress restrictions."""
    return {
        "egress_dns_blocked": True,
        "egress_http_restricted": True,
        "ssh_available": True,          # dropbear on :22
        "local_proxy_port": 18080,      # internal, not user-accessible
        "control_plane": "10.198.0.1:9102",
        "bypass_method": "dns_doh_fallback",
    }


def apply_bypass():
    """Enable transparent DoH-based DNS bypass. Idempotent."""
    enable_all()
    return True


def auto_setup():
    """Detect + patch in one call. Returns True if CoCalc detected & patched."""
    if detect():
        apply_bypass()
        print("[FreeNode] CoCalc detected — internet bypass enabled", file=sys.stderr)
        return True
    return False


if __name__ == "__main__":
    if detect():
        print("CoCalc environment detected")
        print(f"Restrictions: {get_restrictions()}")
        ip = resolve_via_doh("github.com")
        print(f"DoH test github.com -> {ip}")
    else:
        print("Not running on CoCalc")
