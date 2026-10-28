"""
File API handlers for FreeNode Dashboard.

Provides REST endpoints for file operations:
  - Browse directories
  - Read file content
  - Write file content
  - Delete files/directories
  - Upload files
  - Download files
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel


class FileInfo(BaseModel):
    name: str
    path: str
    type: str  # file | directory
    size: int
    modified: float


class FileReadRequest(BaseModel):
    path: str


class FileWriteRequest(BaseModel):
    path: str
    content: str


class FileDeleteRequest(BaseModel):
    path: str


class FileManager:
    """Manages filesystem operations with safety checks."""

    def __init__(self, root: str = None):
        self.root = Path(root or os.getcwd()).resolve()

    def _safe_path(self, path: str) -> Path:
        """Resolve path and ensure it's within root."""
        p = (self.root / path).resolve()
        if not str(p).startswith(str(self.root)):
            raise ValueError("Path outside root directory")
        return p

    def list_directory(self, path: str = ".") -> List[Dict]:
        """List directory contents."""
        safe_path = self._safe_path(path)
        if not safe_path.is_dir():
            raise ValueError("Not a directory")

        items = []
        try:
            for entry in sorted(safe_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "path": str(entry.relative_to(self.root)),
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size if entry.is_file() else 0,
                    "modified": stat.st_mtime,
                })
        except PermissionError:
            raise ValueError("Permission denied")

        return items

    def read_file(self, path: str) -> str:
        """Read file content."""
        safe_path = self._safe_path(path)
        if not safe_path.is_file():
            raise ValueError("Not a file")

        try:
            with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Read error: {e}")

    def write_file(self, path: str, content: str) -> Dict:
        """Write file content."""
        safe_path = self._safe_path(path)

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "ok", "path": str(safe_path.relative_to(self.root))}
        except Exception as e:
            raise ValueError(f"Write error: {e}")

    def delete(self, path: str) -> Dict:
        """Delete file or directory."""
        safe_path = self._safe_path(path)

        try:
            if safe_path.is_dir():
                shutil.rmtree(safe_path)
            else:
                safe_path.unlink()
            return {"status": "deleted", "path": path}
        except Exception as e:
            raise ValueError(f"Delete error: {e}")

    def create_directory(self, path: str) -> Dict:
        """Create a directory."""
        safe_path = self._safe_path(path)

        try:
            safe_path.mkdir(parents=True, exist_ok=True)
            return {"status": "created", "path": str(safe_path.relative_to(self.root))}
        except Exception as e:
            raise ValueError(f"Create error: {e}")
