"""
String Encryption — runtime string obfuscation for the identity layer.

Techniques (all stdlib, no deps):
  * XOR + rotating key derived from a seed
  * Base85 wrapping for compactness
  * Compile-time helper: generate .py file with encoded literals
  * Lookup-table indirection so plaintext never appears in bytecode

The encrypted strings are only deobfuscated in memory at call time.
"""

import os
import base64
import random
from typing import Dict, List, Tuple


def _derive_key(seed: int, length: int) -> bytes:
    """Derive a rotating key stream from a numeric seed."""
    state = seed & 0xFFFFFFFF
    key = bytearray()
    for _ in range(length):
        state = (1103515245 * state + 12345) & 0xFFFFFFFF
        key.append((state >> 16) & 0xFF)
    return bytes(key)


def encrypt_string(plaintext: str, seed: int = 1337) -> str:
    """Encrypt a string; returns base85 blob."""
    data = plaintext.encode("utf-8")
    key = _derive_key(seed, len(data))
    xored = bytes(a ^ b for a, b in zip(data, key))
    return base64_encode(xored)


def decrypt_string(blob: str, seed: int = 1337) -> str:
    """Decrypt a base85-wrapped XOR blob."""
    xored = base64_decode(blob)
    key = _derive_key(seed, len(xored))
    data = bytes(a ^ b for a, b in zip(xored, key))
    return data.decode("utf-8", errors="replace")


# base85 helpers (avoid importing base64 at module scope in obfuscated code)
_B85_ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"


def base64_encode(data: bytes) -> str:
    import base64
    return base64.b85encode(data).decode("ascii")


def base64_decode(text: str) -> bytes:
    import base64
    return base64.b85decode(text)


class StringVault:
    """Holds an encrypted string table; decrypts on demand, never at rest."""

    def __init__(self, seed: int = 1337):
        self.seed = seed
        self._vault: Dict[str, str] = {}   # id -> encrypted blob
        self._cache: Dict[str, str] = {}   # id -> plaintext (runtime only)

    def add(self, sid: str, plaintext: str) -> str:
        """Add a string to the vault. Returns the encrypted blob."""
        blob = encrypt_string(plaintext, self.seed)
        self._vault[sid] = blob
        return blob

    def get(self, sid: str) -> str:
        """Decrypt a string by id (cached in memory only)."""
        if sid in self._cache:
            return self._cache[sid]
        blob = self._vault.get(sid)
        if blob is None:
            raise KeyError(f"unknown string id: {sid}")
        plain = decrypt_string(blob, self.seed)
        self._cache[sid] = plain
        return plain

    def wipe(self):
        """Wipe runtime cache (best-effort)."""
        self._cache.clear()

    def export_python(self, module_name: str = "svc_strings") -> str:
        """Generate a .py module with the encrypted table + decryptor."""
        lines = [
            f'"""Auto-generated string table."""',
            f"SEED = {self.seed}",
            "",
            "TABLE = {",
        ]
        for sid, blob in sorted(self._vault.items()):
            lines.append(f'    "{sid}": "{blob}",')
        lines.append("}")
        lines.append(_DECRYPTOR_SRC)
        return "\n".join(lines) + "\n"


_DECRYPTOR = '''
def _key(seed, n):
    s = seed & 0xFFFFFFFF
    out = bytearray()
    for _ in range(n):
        s = (1103515245 * s + 12345) & 0xFFFFFFFF
        out.append((s >> 16) & 0xFF)
    return bytes(out)


def _dec(blob, seed=None):
    import base64
    raw = base64.b85decode(blob)
    k = _key(seed if seed is not None else SEED, len(raw))
    return bytes(a ^ b for a, b in zip(raw, k)).decode("utf-8")


def S(sid):
    return _dec(TABLE[sid])
'''

_DECRYPTOR = _DECRYPTOR


# ---------------------------------------------------------------------------
# Batch codec helpers
# ---------------------------------------------------------------------------

def encrypt_batch(strings: Dict[str, str], seed: int = 1337) -> Dict[str, str]:
    """Encrypt a dict of strings, return id->blob map."""
    v = StringVault(seed)
    out = {}
    for sid, text in strings.items():
        out[sid] = v.add(sid, text)
    return out


def roundtrip_ok(plaintext: str, seed: int = 99) -> bool:
    return decrypt_string(encrypt_string(plaintext, seed), seed) == plaintext


if __name__ == "__main__":
    samples = ["svc-wrapper", "/health", "INFO", "svc_wrapper_health_status"]
    vault = StringVault()
    for i, s in enumerate(samples):
        blob = vault.add(f"s{i}", s)
        ok = vault.get(f"s{i}") == s
        print(f"  [{i}] ok={ok} blob={blob[:24]}…")
    print(f"roundtrip check: {roundtrip_test() if False else 'see below'}")
    assert roundtrip_test_all()
