"""
Resource Module for FreeNode
=============================
Bypass cgroup, RAM, CPU, and disk quota limitations.
"""

from .resource import Resource

__all__ = ['Resource']

def setup_resource_module() -> dict:
    """Initialize Resource module with default configuration"""
    resource = Resource()
    
    return {
        "status": "ok",
        "resource": resource,
        "cgroup_detected": resource.cgroup_detected,
        "proot_installed": resource.proot_installed,
        "swap_enabled": resource.swap_enabled,
    }
