"""
Terminal WebSocket handler for FreeNode Dashboard.

Provides a full PTY (pseudo-terminal) over WebSocket so the dashboard
can offer a real shell experience (bash/zsh/fish).

Uses pty.spawn for a proper interactive shell with job control,
color support, and readline.
"""

import os
import pty
import select
import subprocess
import struct
import fcntl
import termios
import asyncio
import logging
from typing import Optional

logger = logging.getLogger("freenode.dashboard.terminal")


class Terminal:
    """Manages a PTY session for a WebSocket client."""

    def __init__(self, websocket):
        self.ws = websocket
        self.fd: Optional[int] = None
        self.pid: Optional[int] = None
        self.running = False

    async def start(self, shell: str = None, cwd: str = None):
        """Spawn a shell in a PTY and start I/O loops."""
        shell = shell or os.environ.get("SHELL", "/bin/bash")
        cwd = cwd or os.getcwd()

        # Fork PTY
        pid, fd = pty.fork()
        if pid == 0:
            # Child: exec shell
            os.chdir(cwd)
            os.execvp(shell, [shell])
        else:
            # Parent: manage PTY I/O
            self.pid = pid
            self.fd = fd
            self.running = True
            # Set non-blocking
            flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            # Start I/O tasks
            await asyncio.gather(
                self._read_pty(),
                self._read_ws(),
            )

    async def _read_pty(self):
        """Read from PTY and send to WebSocket."""
        while self.running:
            try:
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if r:
                    data = os.read(self.fd, 4096)
                    if data:
                        await self.ws.send_text(data.decode("utf-8", errors="replace"))
                    else:
                        break
            except OSError:
                break
            await asyncio.sleep(0.01)

    async def _read_ws(self):
        """Read from WebSocket and write to PTY."""
        try:
            async for message in self.ws.iter_text():
                if message.startswith("__resize__:"):
                    # Resize: __resize__:cols,rows
                    _, dims = message.split(":", 1)
                    cols, rows = map(int, dims.split(","))
                    self._resize(cols, rows)
                else:
                    os.write(self.fd, message.encode("utf-8"))
        except Exception as e:
            logger.error(f"WebSocket read error: {e}")
        finally:
            self.running = False

    def _resize(self, cols: int, rows: int):
        """Resize the PTY."""
        try:
            size = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, size)
        except Exception as e:
            logger.warning(f"Resize failed: {e}")

    async def close(self):
        """Clean up PTY and kill shell."""
        self.running = False
        if self.fd:
            try:
                os.close(self.fd)
            except Exception:
                pass
        if self.pid:
            try:
                os.kill(self.pid, 15)
                os.waitpid(self.pid, 0)
            except Exception:
                pass


async def handle_terminal_ws(websocket):
    """WebSocket handler for /api/terminal."""
    terminal = Terminal(websocket)
    try:
        await websocket.accept()
        await terminal.start()
    finally:
        await terminal.close()
