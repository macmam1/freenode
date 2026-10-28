#!/usr/bin/env python3
"""
Test suite for the Obfuscation Layer (v0.2.0).
Run: python3 tests/test_obfuscation.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILURES = []


def check(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
    except Exception as e:
        print(f"  FAIL  {name}: {type(e).__name__}: {e}")
        FAILURES.append(name)


def test_string_encryption():
    from src.obfuscation import StringVault, encrypt_string, decrypt_string

    # roundtrip
    for i, s in enumerate(["svc-wrapper", "/health", "INFO", "us-east-1"]):
        assert decrypt_string(encrypt_string(s, 42 + i), 42 + i) == s, f"roundtrip fail: {s}"

    # vault add/get
    v = StringVault(seed=7)
    v.add("name", "svc-wrapper")
    v.add("path", "/health")
    assert v.get("name") == "svc-wrapper"
    assert v.get("path") == "/health"

    # no plaintext at rest
    blob = v._vault["name"]
    assert "svc-wrapper" not in blob, "plaintext leaked into blob!"

    # batch
    from src.obfuscation import encrypt_batch
    batch = encrypt_batch({"a": "alpha", "b": "beta"}, seed=3)
    assert "alpha" not in batch["a"] and "beta" not in batch["b"]


def test_anti_analysis():
    from src.obfuscation import EnvironmentInspector, QuietMode

    insp = EnvironmentInspector()
    _ = insp.is_interactive()
    _ = insp.container_runtime()
    _ = insp.resource_bounds()
    _ = insp.ptrace_scope()

    q = QuietMode(threshold=99)  # threshold high => never quiet
    score = q.scan()
    assert not q.should_quiet(), f"expected loud, score={score}"


def test_artifact_stripper():
    import re
    from src.obfuscation import ArtifactStripper, BytecodeStripper, PayloadStripper

    # source strip
    src = '# hello\ndef f():\n    """doc"""\n    return 1\n'
    out = BytecodeStripper.strip_source(src)
    assert "#" not in out and "docstring" not in out, "docstring/comment survived"

    # payload marker zeroing
    dirty = b"some data freenode marker FreeNode tail"
    cleaned = PayloadStripper.strip_exif_like(dirty)
    assert b"freenode" not in cleaned.lower(), "marker survived"

    # file ops in temp dir
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td := td if False else td, "x.log")
        with open(os.path.join(td, "x.log"), "w") as f:
            f.write("sensitive freenode line\n")
        st = ArtifactStripper(td)
        n = st.strip_logs()
        assert n == 1
        assert os.path.getsize(os.path.join(td, "x.log")) == 0

        with open(os.path.join(td, "meta.txt"), "w") as f:
            f.write("freenode secret")
        st.zero_timestamps()
        pat = [(re.compile("freenode", re.I), "svc")]
        assert st.scrub_text_file(os.path.join(td, "meta.txt"), pat)
        with open(os.path.join(td, "meta.txt")) as f:
            assert "freenode" not in f.read().lower()


def test_cross_layer_integration():
    """Deception + Obfuscation work together."""
    from src.deception import MetadataCleaner, LogScrubber, detect_platform
    from src.obfuscation import StringVault, QuietMode

    platform = detect_platform()
    assert isinstance(platform, str)

    # vault encrypts identity strings
    v = StringVault(seed=2026)
    v.add("identity", "svc-wrapper")
    assert v.get("identity") == "svc-wrapper"

    # scrubber cleans any accidental leak
    s = LogScrubber()
    text = s.scrub("ssh tunnel credentials bypass")
    for word in ("ssh", "tunnel", "credentials", "bypass"):
        assert word not in text, f"'{word}' survived scrubbing"

    # quiet mode is a bool
    q = QuietMode(threshold=99)
    assert isinstance(q.should_quiet(), bool)


def main():
    print("Obfuscation Layer tests")
    print("=" * 50)
    check("string_encryption", test_string_encryption)
    check("anti_analysis", test_anti_analysis)
    check("artifact_stripper", test_artifact_stripper)
    check("cross_layer_integration", test_cross_layer_integration)
    print("=" * 50)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} -> {FAILURES}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
