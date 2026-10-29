"""
FreeNode Terminal Modules
Provides headless terminal access independent of browser sessions
"""

from .tmate_headless import TmateHeadlessManager

__all__ = [
    "TmateHeadlessManager",
]
