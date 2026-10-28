from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import subprocess
import json
import os

app = FastAPI(title="FreeNode API", version="1.0.0")

class Command(BaseModel):
    command: str
    cwd: Optional[str] = None

class FileWrite(BaseModel):
    path: str
    content: str

@app.get("/")
def read_root():
    return {"service": "freenode-api", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/exec")
def exec_command(cmd: Command):
    try:
        result = subprocess.run(
            cmd.command, 
            shell=True,
            cwd=cmd.cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/write")
def write_file(fw: FileWrite):
    try:
        with open(fw.path, 'w') as f:
            f.write(fw.content)
        return {"status": "ok", "path": fw.path}
    except Exception as e:
        return {"error": str(e)}

@app.get("/env")
def get_env():
    safe_vars = {}
    for k, v in os.environ.items():
        if not any(s in k.upper() for s in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'AUTH']):
            safe_vars[k] = v
    return safe_vars

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
