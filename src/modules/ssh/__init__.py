"""
SSH Module for FreeNode
=======================
Provides SSH server installation, key management, and reverse tunneling.
"""

from .sshd import SSHD
from .key_manager import KeyManager
from .reverse import ReverseTunnel

__all__ = ['SSHD', 'KeyManager', 'ReverseTunnel']

def setup_ssh_module() -> dict:
    """Initialize SSH module with default configuration"""
    sshd = SSHD()
    keys = KeyManager()
    tunnel = ReverseTunnel()

    result = {
        "status": "ok",
        "sshd": sshd,
        "key_manager": keys,
        "reverse_tunnel": tunnel,
    }
    return result
