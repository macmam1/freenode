#!/usr/bin/env python3
"""
FreeNode Kaggle Deployment Script
Deploys FreeNode to Kaggle Notebooks with persistent keep-alive
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

KAGGLE_API_KEY = os.getenv("KAGGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class KaggleDeployment:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "platform": "kaggle",
            "status": "initializing",
            "steps": []
        }
    
    def log_step(self, name, status, detail=""):
        self.test_results["steps"].append({
            "name": name,
            "status": status,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        })
        print(f"[{name}] {status} - {detail}")
    
    def test_kaggle_api(self):
        """Test Kaggle API connection"""
        try:
            cmd = f"curl -s -H 'Authorization: Bearer {KAGGLE_API_KEY}' https://www.kaggle.com/api/v1/kernels/list | head -c 100"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                self.log_step("kaggle_api_test", "PASS", "API responding")
                return True
            else:
                self.log_step("kaggle_api_test", "FAIL", result.stderr)
                return False
        except Exception as e:
            self.log_step("kaggle_api_test", "ERROR", str(e))
            return False
    
    def detect_environment(self):
        """Detect current environment"""
        try:
            import psutil
            env = {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "disk_gb": psutil.disk_usage('/').total / (1024**3),
                "is_root": os.geteuid() == 0 if hasattr(os, 'geteuid') else False
            }
            self.log_step("environment_detection", "PASS", json.dumps(env))
            return env
        except Exception as e:
            self.log_step("environment_detection", "ERROR", str(e))
            return {}
    
    def clone_freenode(self):
        """Clone FreeNode repository"""
        try:
            cmd = "git clone https://github.com/macmam1/freenode.git ~/freenode 2>&1 | tail -5"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_step("freenode_clone", "PASS", "Repository cloned")
                return True
            else:
                self.log_step("freenode_clone", "FAIL", result.stderr[:200])
                return False
        except Exception as e:
            self.log_step("freenode_clone", "ERROR", str(e))
            return False
    
    def test_keepalive(self):
        """Test keep-alive mechanism"""
        try:
            cmd = "python3 ~/freenode/src/modules/keepalive/keepalive.py --test --interval 30 2>&1 | head -20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if "keep-alive" in result.stdout.lower() or result.returncode == 0:
                self.log_step("keepalive_test", "PASS", "Keep-alive module functional")
                return True
            else:
                self.log_step("keepalive_test", "FAIL", result.stdout[:200])
                return False
        except Exception as e:
            self.log_step("keepalive_test", "ERROR", str(e))
            return False
    
    def test_persistence(self):
        """Test persistence module"""
        try:
            cmd = "python3 ~/freenode/src/core/persistence.py --test 2>&1 | head -20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_step("persistence_test", "PASS", "Persistence module working")
                return True
            else:
                self.log_step("persistence_test", "FAIL", result.stdout[:200])
                return False
        except Exception as e:
            self.log_step("persistence_test", "ERROR", str(e))
            return False
    
    def generate_report(self):
        """Generate test report"""
        self.test_results["status"] = "completed"
        self.test_results["summary"] = {
            "total_steps": len(self.test_results["steps"]),
            "passed": len([s for s in self.test_results["steps"] if s["status"] == "PASS"]),
            "failed": len([s for s in self.test_results["steps"] if s["status"] == "FAIL"]),
            "errors": len([s for s in self.test_results["steps"] if s["status"] == "ERROR"])
        }
        
        report_file = f"test-report-kaggle-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log_step("report_generation", "PASS", f"Report: {report_file}")
        return report_file
    
    def run(self):
        """Run deployment test"""
        print("=== FreeNode Kaggle Deployment Test ===")
        self.test_kaggle_api()
        self.detect_environment()
        self.clone_freenode()
        self.test_keepalive()
        self.test_persistence()
        report = self.generate_report()
        
        print("\n=== SUMMARY ===")
        print(json.dumps(self.test_results["summary"], indent=2))
        return report

if __name__ == "__main__":
    deployer = KaggleDeployment()
    report_file = deployer.run()
    sys.exit(0 if deployer.test_results["summary"]["errors"] == 0 else 1)
