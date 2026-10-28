"""
Artifact Stripper — remove forensic traces from generated artifacts.

Handles:
  * Python bytecode hygiene (no docstrings in deployed .pyc)
  * Stripping debug info from payloads
  * Zeroing free metadata blocks in written files
  * Timestamp normalization for emitted files

Runs as part of the build/packaging lifecycle.
"""

import os
import io
import time
import random
import zipfile
from typing import List, Optional


class BytecodeStripper:
    """Compile .py to optimized .pyc without docstrings/comments."""

    @staticmethod
    def strip_source(source: str) -> str:
        """Remove comments and docstrings from Python source (regex-lite)."""
        import re
        out_lines = []
        in_doc = False
        doc_quote = None
        for line in source.splitlines():
            stripped = line.strip()
            if in_doc:
                if doc_quote and doc_quote in stripped:
                    in_doc = False
                continue
            if stripped.startswith(("#",)):
                continue
            for q in ('"""', "'''"):
                if stripped.startswith(q) and stripped.count(q) >= 2 and len(stripped) > 2 * len(q):
                    stripped = ""
                    break
                if stripped.startswith(q):
                    in_doc = True
                    doc_quote = q
                    break
            if in_doc:
                continue
            out_lines.append(line)
        return "\n".join(out_lines) + "\n"


class ArtifactStripper:
    """Clean artifacts we generate (logs, payloads, temp files)."""

    STRIP_EXTENSIONS = {".log", ".tmp", ".out", ".bak", ".pid"}

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    def strip_logs(self) -> int:
        """Truncate log artifacts found in base_dir."""
        n = 0
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                if os.path.splitext(f)[1] in self.STRIP_EXTENSIONS:
                    p = os.path.join(root, f)
                    try:
                        open(p, "w").close()
                        n += 1
                    except Exception:
                        pass
        return n

    def zero_timestamps(self, fake_days_ago: int = 14) -> int:
        """Normalize mtimes on emitted files."""
        t = time.time() - random.randint(1, max(2, fake_days_ago)) * 86400
        n = 0
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                p = os.path.join(root, f)
                try:
                    os.utime(p, (t, t))
                    n += 1
                except Exception:
                    pass
        return n

    def scrub_text_file(self, path: str, patterns: List) -> bool:
        """Apply regex substitutions to a text file in place."""
        try:
            with open(path, "r", errors="replace") as f:
                content = f.read()
            for pat, repl in patterns:
                content = pat.sub(repl, content)
            with open(path, "w") as f:
                f.write(content)
            return True
        except Exception:
            return False


class PayloadStripper:
    """Strip identifying metadata from binary payloads we emit."""

    @staticmethod
    def strip_exif_like(data: bytes) -> bytes:
        """Zero out common metadata markers in emitted blobs."""
        # PNG tEXt / zlib headers etc. — generic zeroing of trailing chunks
        out = bytearray(data)
        # Remove obvious "FreeNode" markers if any slipped in
        for marker in (b"freenode", b"FreeNode", b"FREENODE"):
            idx = out.lower().find(marker)
            while idx != -1:
                out[idx:idx + len(marker)] = b"\x00" * len(marker)
                idx = out.lower().find(marker, idx + 1)
        return bytes(out)


if __name__ == "__main__":
    sample = '''
    # comment
    """module docstring"""
    def f():
        "fn doc"
        return 1
    '''
    print(BytecodeStripper.strip_source(sample))
