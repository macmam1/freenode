"""
Dashboard — Web-based control plane for FreeNode.

Provides:
  - FastAPI web app serving a minimal UI
  - REST endpoints for module management, status, config, deploy, pack, quiet
  - Static frontend (HTML/CSS/JS) — minimal but functional

Endpoints:
  GET  /                -> serve dashboard UI
  GET  /api/status     -> current status
  GET  /api/modules    -> list modules
  POST /api/modules/{name}/enable
  POST /api/modules/{name}/disable
  POST /api/deploy     -> run full deploy
  POST /api/pack       -> pack artifacts
  POST /api/quiet      -> toggle quiet
  GET  /api/config     -> get config
  POST /api/config     -> update config
"""

from .app import app, start

__all__ = ["app", "start"]
