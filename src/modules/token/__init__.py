"""
Token Module for FreeNode
=========================
Capture, inject, refresh, and persist API tokens.
"""

from .token import TokenManager

__all__ = ['TokenManager']

def setup_token_module() -> dict:
    """Initialize Token module"""
    tm = TokenManager()
    summary = tm.capture_all()

    return {
        "status": "ok",
        "token_manager": tm,
        "total_captured": summary["total"],
        "env_tokens": list(summary["captured_env"].keys()),
        "files_scanned": list(summary["captured_files"].keys()),
    }
