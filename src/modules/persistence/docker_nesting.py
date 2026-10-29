"""
FreeNode Docker Nesting Manager
Runs FreeNode inside a nested Docker container with --restart unless-stopped
Based on vps-deploy pattern from hopingboyz/vps-deploy
"""
import subprocess
import logging
import asyncio
import json
from typing import Optional

logger = logging.getLogger("freenode.persistence.docker")


class DockerNestingManager:
    """Manages FreeNode inside a nested Docker container"""
    
    def __init__(self, container_prefix: str = "freenode-",
                 image: str = "ubuntu:22.04",
                 memory: str = "2g",
                 cpus: str = "1"):
        self.container_prefix = container_prefix
        self.container_name = f"{container_prefix}agent"
        self.image = image
        self.memory = memory
        self.cpus = cpus
        
    def is_docker_available(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(["docker", "--version"],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def container_exists(self) -> bool:
        """Check if the container already exists"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=5
            )
            return self.container_name in result.stdout
        except Exception:
            return False
    
    def start(self) -> bool:
        """Start FreeNode in a nested Docker container with auto-restart"""
        if not self.is_docker_available():
            logger.error("Docker not available")
            return False
        
        try:
            # Remove existing container if it exists
            if self.container_exists():
                logger.info(f"Removing existing container {self.container_name}")
                subprocess.run(["docker", "rm", "-f", self.container_name],
                             capture_output=True, timeout=10)
            
            # Build docker run command
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "--restart", "unless-stopped",
                "--privileged",
                "--cap-add=ALL",
                "--memory", self.memory,
                "--cpus", self.cpus,
                "-v", "/opt/freenode:/opt/freenode",
                "-v", "/var/run/docker.sock:/var/run/docker.sock",
                "-e", "FREENODE_NESTED=1",
                self.image,
                "/bin/bash", "-c",
                "sleep infinity"  # Keep container alive
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Docker run failed: {result.stderr}")
                return False
            
            container_id = result.stdout.strip()
            logger.info(f"✅ Docker nesting started: {container_id}")
            return True
            
        except Exception as e:
            logger.error(f"Docker nesting error: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the nested Docker container"""
        if not self.is_docker_available():
            return False
        
        try:
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info(f"✅ Docker container {self.container_name} stopped")
                return True
            else:
                logger.error(f"stop failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Docker stop error: {e}")
            return False
    
    def status(self) -> dict:
        """Get container status"""
        if not self.is_docker_available():
            return {"docker_available": False}
        
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{json .}}", "--filter", f"name={self.container_name}"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Container is running
                containers = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                if containers:
                    container = containers[0]
                    return {
                        "docker_available": True,
                        "running": True,
                        "container_id": container.get("ID", "unknown")[:12],
                        "status": container.get("Status", "unknown"),
                        "uptime": container.get("RunningFor", "unknown")
                    }
            
            # Check if container exists but is stopped
            result_all = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{json .}}", "--filter", f"name={self.container_name}"],
                capture_output=True, text=True, timeout=5
            )
            
            if result_all.returncode == 0 and result_all.stdout.strip():
                containers = [json.loads(line) for line in result_all.stdout.strip().split('\n') if line]
                if containers:
                    container = containers[0]
                    return {
                        "docker_available": True,
                        "running": False,
                        "exists": True,
                        "status": container.get("Status", "unknown")
                    }
            
            return {
                "docker_available": True,
                "running": False,
                "exists": False
            }
        except Exception as e:
            logger.error(f"status check failed: {e}")
            return {"docker_available": True, "error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mgr = DockerNestingManager()
    print(f"Docker available: {mgr.is_docker_available()}")
    print(f"Status: {mgr.status()}")
