"""
Deception Layer — v0.1.0
Masks FreeNode as a legitimate service wrapper on every platform.

Modules:
  - installation_spoof: benign install output & decoy files
  - platform_presentation: process / network / filesystem identity
  - traffic_normalizer: human-like timing, payload, DNS, TLS
  - package_wrapper: decoy pip/npm package generation
  - metadata_cleaner: scrub traces from logs, build, git, timestamps (56+ patterns)
  - behavioral_mimicry: health checks, metrics, signals, log rotation, graceful shutdown
"""

from .installation_spoof import InstallationSpoof, DECOY_NAMES
from .platform_presentation import (
    ProcessPresentation,
    NetworkPresentation,
    FilesystemPresentation,
    PLATFORM_PROFILES,
    detect_platform,
)
from .traffic_normalizer import (
    TrafficNormalizer,
    TrafficConfig,
    TimingNormalizer,
    PayloadObfuscator,
    DNSNormalizer,
    TLSNormalizer,
    NormalizedRequest,
)
from .package_wrapper import PackageWrapper, PACKAGE_PROFILES
from .metadata_cleaner import (
    MetadataCleaner,
    FilesystemCleaner,
    LogScrubber,
    ProcessSanitizer,
    GitMetadataNormalizer,
    SENSITIVE_PATTERNS,
)
from .behavioral_mimicry import (
    BehavioralMimicry,
    BehavioralProfile,
    PLATFORM_BEHAVIORS,
    detect_behavior_platform,
)

__all__ = [
    # installation_spoof
    "InstallationSpoof",
    "DECOY_NAMES",
    # platform_presentation
    "ProcessPresentation",
    "NetworkPresentation",
    "FilesystemPresentation",
    "PLATFORM_PROFILES",
    "detect_platform",
    # traffic_normalizer
    "TrafficNormalizer",
    "TrafficConfig",
    "TimingNormalizer",
    "PayloadObfuscator",
    "DNSNormalizer",
    "TLSNormalizer",
    "NormalizedRequest",
    # package_wrapper
    "PackageWrapper",
    "PACKAGE_PROFILES",
    # metadata_cleaner
    "MetadataCleaner",
    "FilesystemCleaner",
    "LogScrubber",
    "ProcessSanitizer",
    "GitMetadataNormalizer",
    "SENSITIVE_PATTERNS",
    # behavioral_mimicry
    "BehavioralMimicry",
    "BehavioralProfile",
    "PLATFORM_BEHAVIORS",
    "detect_behavior_platform",
]

__version__ = "0.1.0"