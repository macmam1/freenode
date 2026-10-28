"""
FreeNode Version Information
=============================
Versioning follows a strict patch-based system:

    0.0.X → Minor additions, bug fixes, module refinements
    0.1.0 → Major module addition (ssh, resource, privilege)
    1.0.0 → MVP Complete — All modules functional + initial test runs
"""

VERSION = "0.2.0"
NAME = "freenode"
BUILD = "dev"

CHANGELOG = {
    "0.2.0": [
        "obfuscation: string_encryption (XOR+base85 vault, compile-time table generator)",
        "obfuscation: anti_analysis (read-only env hygiene, adaptive quiet mode)",
        "obfuscation: artifact_stripper (log truncation, timestamp normalization, marker zeroing)",
        "deception: behavioral_mimicry (health/metrics/signals/log rotation, 8 platform profiles)",
        "deception: metadata_cleaner extended to 56 sensitive patterns (net/proc/fs/runtime)",
        "tests: test_obfuscation.py + test_behavioral_mimicry.py (both green)",
    ],
    "0.0.2": [
        "resource: complete proot install + cgroup bypass + swap management + memory optimize",
        "privilege: sudo/proot/su/capability escalation + sudoers management",
        "token: full capture from env + files + inject + refresh + persist",
        "all __init__.py modules created with setup_* functions",
        "privilege.py: added missing shutil import",
        "token.py: added missing Path import",
    ],
    "0.0.1": [
        "ssh: complete module (sshd + key_manager + reverse tunnel)",
        "version.py created with versioning policy",
    ],
}
