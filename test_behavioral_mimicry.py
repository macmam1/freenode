#!/usr/bin/env python3
"""
Safe test for behavioral_mimicry module.
No system commands, just import and instantiate.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_behavioral_mimicry():
    """Test behavioral mimicry module."""
    try:
        from src.deception.behavioral_mimicry import (
            BehavioralMimicry,
            PLATFORM_BEHAVIORS,
            detect_behavior_platform,
        )
        
        print("✅ Import successful\n")
        
        # Test platform detection
        platform = detect_behavior_platform()
        print(f"📍 Detected platform: {platform}")
        
        # Test instantiation for all platforms
        platforms_to_test = ["render", "railway", "fly", "modal", "replit", "kaggle", "colab"]
        
        for p in platforms_to_test:
            bm = BehavioralMimicry(platform=p)
            state = bm.start()
            print(f"\n  {p.upper()}:")
            print(f"    Health path: {bm.profile.health_path}")
            print(f"    Health interval: {bm.profile.health_interval}s")
            print(f"    Metrics enabled: {bm.profile.metrics_enabled}")
            print(f"    Log file: {bm.profile.log_file}")
            print(f"    Shutdown grace: {bm.profile.shutdown_grace}s")
            print(f"    SIGHUP action: {bm.profile.sighup_action}")
        
        # Test health response
        bm = BehavioralMimicry("render")
        health = bm.health_response()
        print(f"\n✅ Health response: {health['status']} (v{health['version']})")
        
        # Test metrics response
        metrics = bm.metrics_response()
        print(f"✅ Metrics response length: {len(metrics)} bytes")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_behavioral_mimicry()
    sys.exit(0 if success else 1)
