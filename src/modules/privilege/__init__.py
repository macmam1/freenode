"""
Privilege Module for FreeNode
==============================
Privilege escalation, sudoers management, Linux capabilities.
"""

from .privilege import Privilege

__all__ = ['Privilege']

def setup_privilege_module() -> dict:
    """Initialize Privilege module"""
    priv = Privilege()
    
    return {
        "status": "ok",
        "privilege": priv,
        "current_user": priv.user,
        "current_uid": priv.user_id,
        "escalated": priv.escalated,
    }
