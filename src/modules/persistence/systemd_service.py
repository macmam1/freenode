"""
FreeNode Systemd Service Manager
Installs and manages FreeNode as a systemd service with auto-restart
Based on hvm-panel pattern from hopingboyz/hvm-panel
"""
import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger("freenode.persistence.systemd")


class SystemdServiceManager:
    """Manages FreeNode as a persistent systemd service"""
    
    def __init__(self, service_name: str = "freenode-daemon",
                 binary_path: str = "/opt/freenode/freenode-daemon",
                 log_path: str = "/var/log/freenode-daemon.log"):
        self.service_name = service_name
        self.binary_path = binary_path
        self.log_path = log_path
        self.service_file = f"/etc/systemd/system/{service_name}.service"
        
    def is_available(self) -> bool:
        """Check if systemd is available on this system"""
        return os.path.exists("/run/systemd/system")
    
    def install(self) -> bool:
        """Install FreeNode as systemd service with Restart=always"""
        if not self.is_available():
            logger.error("systemd not available on this system")
            return False
        
        service_content = f"""[Unit]
Description=FreeNode Persistent Daemon
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart={self.binary_path}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
"""
        try:
            # Write service file
            with open(self.service_file, "w") as f:
                f.write(service_content)
            logger.info(f"✅ Wrote service file: {self.service_file}")
            
            # Reload systemd daemon
            result = subprocess.run(["systemctl", "daemon-reload"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.error(f"daemon-reload failed: {result.stderr}")
                return False
            
            # Enable service
            result = subprocess.run(["systemctl", "enable", self.service_name],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.error(f"enable failed: {result.stderr}")
                return False
            
            logger.info(f"✅ systemd service '{self.service_name}' installed and enabled")
            return True
        except Exception as e:
            logger.error(f"systemd install failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start the systemd service"""
        if not self.is_available():
            logger.error("systemd not available")
            return False
        
        try:
            result = subprocess.run(["systemctl", "start", self.service_name],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ systemd service '{self.service_name}' started")
                return True
            else:
                logger.error(f"start failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"systemd start error: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the systemd service"""
        if not self.is_available():
            return False
        
        try:
            result = subprocess.run(["systemctl", "stop", self.service_name],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ systemd service '{self.service_name}' stopped")
                return True
            else:
                logger.error(f"stop failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"systemd stop error: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the systemd service"""
        if not self.is_available():
            return False
        
        try:
            result = subprocess.run(["systemctl", "restart", self.service_name],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ systemd service '{self.service_name}' restarted")
                return True
            else:
                logger.error(f"restart failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"systemd restart error: {e}")
            return False
    
    def status(self) -> dict:
        """Get systemd service status"""
        if not self.is_available():
            return {"available": False, "running": False}
        
        try:
            result = subprocess.run(["systemctl", "is-active", self.service_name],
                                  capture_output=True, text=True, timeout=10)
            is_running = result.stdout.strip() == "active"
            
            result_enabled = subprocess.run(["systemctl", "is-enabled", self.service_name],
                                          capture_output=True, text=True, timeout=10)
            is_enabled = result_enabled.stdout.strip() == "enabled"
            
            return {
                "available": True,
                "running": is_running,
                "enabled": is_enabled,
                "service": self.service_name
            }
        except Exception as e:
            logger.error(f"status check failed: {e}")
            return {"available": True, "running": False, "error": str(e)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mgr = SystemdServiceManager()
    print(f"systemd available: {mgr.is_available()}")
    print(f"status: {mgr.status()}")
