import os
import socket
import psutil
import platform
import requests
import json

class Detector:
    """14-Dimension Environment Discovery for FreeNode"""
    
    def __init__(self):
        self.results = {}

    def detect_all(self):
        self.results['os'] = platform.system()
        self.results['node'] = platform.node()
        self.results['release'] = platform.release()
        self.results['arch'] = platform.machine()
        self.results['cpu_count'] = psutil.cpu_count()
        self.results['memory_total'] = psutil.virtual_memory().total / (1024**3) # GB
        self.results['disk_total'] = psutil.disk_usage('/').total / (1024**3) # GB
        
        # Detection logic
        self.results['is_container'] = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
        self.results['is_root'] = os.geteuid() == 0
        self.results['has_systemd'] = os.path.exists('/run/systemd/system')
        
        # Network detection
        self.results['public_ip'] = self.get_public_ip()
        self.results['hostname'] = socket.gethostname()
        
        # Platform Specifics
        self.results['is_colab'] = 'COLAB_GPU' in os.environ
        self.results['is_kaggle'] = 'KAGGLE_KERNEL_RUN_TYPE' in os.environ
        self.results['is_render'] = 'RENDER' in os.environ
        self.results['is_railway'] = 'RAILWAY_STATIC_URL' in os.environ
        self.results['is_cocalc'] = self._detect_cocalc()
        
        return self.results

    def _detect_cocalc(self):
        """Detect CoCalc environment (project container)"""
        indicators = [
            os.path.exists('/opt/cocalc'),
            os.path.exists('/opt/cocalc/project-bundle'),
            os.path.exists('/home/user/.local/share/cocalc'),
        ]
        return sum(indicators) >= 2

    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org', timeout=5).text
        except:
            return "unknown"

if __name__ == "__main__":
    detector = Detector()
    print(json.dumps(detector.detect_all(), indent=4))
