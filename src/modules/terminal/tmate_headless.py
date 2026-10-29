"""
FreeNode Tmate Headless Terminal Manager
Runs tmate in a headless container for persistent web terminal access
Based on vps-deploy pattern from hopingboyz/vps-deploy
"""
import subprocess
import logging
import asyncio
import re
from typing import Optional, Tuple

logger = logging.getLogger("freenode.terminal.tmate")


class TmateHeadlessManager:
    """Manages headless tmate terminal sessions"""
    
    def __init__(self, container_name: str = "freenode-agent"):
        self.container_name = container_name
        self.session_name = None
        self.ssh_url = None
        self.web_url = None
    
    def is_tmate_installed(self) -> bool:
        """Check if tmate is available in the target container"""
        try:
            result = subprocess.run(
                ["docker", "exec", self.container_name, "which", "tmate"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def install_tmate(self) -> bool:
        """Install tmate inside the container"""
        try:
            install_cmd = "apt-get update && apt-get install -y tmate openssh-client curl wget"
            
            result = subprocess.run(
                ["docker", "exec", self.container_name, "bash", "-c", install_cmd],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"✅ tmate installed in {self.container_name}")
                return True
            else:
                logger.error(f"tmate install failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"tmate install error: {e}")
            return False
    
    async def start_session(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Start a headless tmate session and extract connection URLs"""
        if not self.is_tmate_installed():
            logger.info("tmate not found, installing...")
            if not self.install_tmate():
                return False, None, None
        
        try:
            # Start tmate in new socket with automatic URL capture
            start_cmd = (
                "tmate -F -s freenode new-session -d -x 200 -y 50 "
                "&& sleep 2 "
                "&& tmate display -p '#{client_tty}' "
                "&& tmate display -p '#{tmate_version}' "
                "&& tmate list-sessions"
            )
            
            proc = await asyncio.create_subprocess_exec(
                "docker", "exec", self.container_name, "bash", "-c", start_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            
            if proc.returncode != 0:
                logger.error(f"tmate start failed: {stderr.decode()}")
                return False, None, None
            
            output = stdout.decode().strip()
            logger.info(f"tmate output:\n{output}")
            
            # Parse tmate session info
            self.session_name = "freenode"
            
            # Try to get SSH connection string from tmate
            ssh_url = self._extract_tmate_url(output, "ssh")
            web_url = self._extract_tmate_url(output, "web")
            
            if ssh_url:
                self.ssh_url = ssh_url
                logger.info(f"✅ Tmate SSH: {ssh_url}")
            
            if web_url:
                self.web_url = web_url
                logger.info(f"✅ Tmate Web: {web_url}")
            
            return True, ssh_url, web_url
            
        except asyncio.TimeoutError:
            logger.error("tmate start timeout")
            return False, None, None
        except Exception as e:
            logger.error(f"tmate start error: {e}")
            return False, None, None
    
    def _extract_tmate_url(self, output: str, url_type: str = "ssh") -> Optional[str]:
        """Extract SSH or web URL from tmate output"""
        if url_type == "ssh":
            # Look for ssh://... pattern
            match = re.search(r'ssh://[^\s]+', output)
            if match:
                return match.group(0)
        elif url_type == "web":
            # Look for https://... pattern
            match = re.search(r'https://[^\s]+', output)
            if match:
                return match.group(0)
        
        return None
    
    def get_urls(self) -> dict:
        """Get current session URLs"""
        return {
            "session": self.session_name,
            "ssh": self.ssh_url,
            "web": self.web_url
        }
    
    def stop_session(self) -> bool:
        """Kill the tmate session"""
        try:
            result = subprocess.run(
                ["docker", "exec", self.container_name, "tmate", "kill-session", "-t", "freenode"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ tmate session stopped")
                self.session_name = None
                self.ssh_url = None
                self.web_url = None
                return True
            else:
                logger.error(f"stop failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"tmate stop error: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    mgr = TmateHeadlessManager()
    print(f"tmate installed: {mgr.is_tmate_installed()}")
    
    # To use async:
    # loop = asyncio.get_event_loop()
    # success, ssh, web = loop.run_until_complete(mgr.start_session())
    # print(f"Started: {success}, SSH: {ssh}, Web: {web}")
