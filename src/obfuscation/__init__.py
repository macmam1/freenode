"""
Obfuscation Layer — v0.2.0
Reduces identifiability of FreeNode artifacts at rest and in transit.

Modules:
  - string_encryption: XOR+base85 vault, compile-time table generator
  - anti_analysis: read-only environment hygiene + adaptive quiet mode
  - artifact_stripper: log truncation, timestamp normalization, marker zeroing
"""

from .string_encryption import (
    StringVault,
    encrypt_string,
    decrypt_string,
    encrypt_batch,
)
from .anti_analysis import (
    EnvironmentInspector,
    QuietMode,
)
from .artifact_stripper import (
    ArtifactStripper,
    BytecodeStripper,
    PayloadStripper,
)

__all__ = [
    # string_encryption
    "StringVault",
    "encrypt_string",
    "decrypt_string",
    "encrypt_batch",
    # anti_analysis
    "EnvironmentInspector",
    "QuietMode",
    # artifact_stripper
    "ArtifactStripper",
    "BytecodeStripper",
    "PayloadStripper",
]

__version__ = "0.2.0"
