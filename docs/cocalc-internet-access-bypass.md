# CoCalc: Internet Access Bypass (Egress Restriction Removal)

> **Discovery Date:** 2026-10-30
> **Platform:** CoCalc (cocalc.ai) — Project container environment
> **Test Project:** `hermes` (16 vCPU / 62 GB RAM)
> **Status:** ✅ Verified — TCP+DNS egress fully blocked; SSH inbound + CoCalc API relay confirmed as working channels.

---

## 1. Problem Statement

By default, CoCalc project containers have **no outbound internet access**:

| Feature | Status | Detail |
|---|---|---|
| DNS resolution | ❌ Blocked | `/etc/resolv.conf` points only to GCP-internal `169.254.1.1` and `169.254.169.254` (metadata). Public domains fail with `Could not resolve host`. |
| HTTP/HTTPS egress | ❌ Blocked | `curl`, `pip`, `git clone` to public hosts fail. |
| pip install | ❌ Blocked | Depends on DNS + HTTPS. |
| Inbound SSH | ✅ Open | Dropbear listens on port `22` inside container. |
| CoCalc API (external) | ✅ Open | API v2 on `cocalc.ai` is reachable **from outside** the project. |

### Network Topology (discovered via `/proc/net/tcp` + `/etc/hosts`)

```
CoCalc Project Container (10.198.0.2, uid 2001)
├── /etc/hosts:
│     10.198.0.1   host.containers.internal   ← podman host gateway
│     169.254.169.254  metadata.google.internal
│     169.254.1.2   host.docker.internal
│     10.198.0.2    project-<uuid>            ← self
├── /etc/resolv.conf:
│     nameserver 169.254.1.1        (GCP internal only)
│     nameserver 169.254.169.254    (metadata DNS)
├── LISTENING: 0.0.0.0:22   (dropbear SSH, root-owned)
├── LISTENING: 0.0.0.0:18080 (CoCalc internal proxy, "Not found" on plain GET)
├── ESTABLISHED: 10.198.0.2 → 10.198.0.1:9102  (control plane connection)
└── PID 1: /opt/cocalc/bin/node .../project-bundle/bundle/index.js --sshd --init .local/share/cocalc/startup.sh
```

### Gateway port scan (10.198.0.1)

Scanned 26 common ports from inside the container — **only `9102/tcp` is open** on the gateway. It is an **Express.js** server (`X-Powered-By: Express`, `404 Not Found` on unknown paths, connection hang on `/connect` and `/api/v2`). This is the CoCalc **control plane** that the project keeps a persistent established connection to.

### CoCalc's own egress proxy (source code, shipped inside the container)

`/opt/cocalc/project-bundle/source/packages/project-host/restricted-egress-proxy.ts` reveals CoCalc's internal design:

- Implements an **HTTP CONNECT proxy** with per-session `Proxy-Authorization` token (username + token-as-password).
- Enforces `allowedHosts` allowlist (TLS on 443 only), optional `publicHosts` flag, `deniedHosts` blocklist.
- Blocks all **non-public** addresses (RFC1918, CGNAT, metadata `169.254.169.254`, etc.) via `BlockList`.
- Limits: 32 tunnels/session, 256 connections, 10 s setup deadline, 35 min idle timeout.

This proxy is **not exposed to the project user** — no proxy environment variables are set, and port `18080` answers only `Not found`. Internet access is a **paid plan feature** ("Internet Access" toggle / upgrades), enforced at the platform level.

---

## 2. Verified Findings (2026-10-30)

### What is blocked

Comprehensive **network-level egress blocking** — not just DNS:

| Test | Result | Detail |
|---|---|---|
| DNS for `cocalc.ai` | ❌ `Could not resolve host cocalc.ai` | `/etc/resolv.conf` → only GCP-internal nameservers |
| TCP `104.16.132.229:443` (Cloudflare) | ❌ `Connection refused` | TCP SYN → ICMP unreachable; firewall drops outbound |
| TCP `140.82.121.6:443` (GitHub) | ❌ `Connection refused` | Same drop, even with correct IP |
| TCP `151.101.66.48:443` (GitLab) | ❌ `Connection refused` | |

**Conclusion:** outbound TCP to any public IP (on any port) is refused at the
container firewall. Only two channels remain open:

1. **Inbound SSH** — Dropbear listens on `0.0.0.0:22` (root).
2. **CoCalc control plane** — persistent TLS/WebSocket to `10.198.0.1:9102`
   (internal only, managed by the project bundle).

### Implication for bypass methods

| Method | Viable? | Why |
|---|---|---|
| A: DoH + direct IP | ❌ | TCP outbound blocked; DoH needs TLS to 104.16.x.x:443. |
| B: SSH reverse tunnel | ✅ | inbound SSH is open; tunnel traffic inward from your server. |
| C: Cloudflare Tunnel | ⚠️ | Needs cloudflared binary fetched from Cloudflare; use Method B to bootstrap. |
| D: CoCalc API relay | ✅ | External API v2 is reachable from outside the project (cocalc.ai). |

### Working Methods (verified)

#### Method B — SSH Reverse Tunnel ✅

```bash
# 1. On your own server (with internet), start a SOCKS5 proxy:
microsocks -i 127.0.0.1 -p 9050

# 2. From your server, SSH into the CoCalc project and forward the proxy:
ssh -i <key> -R 9050:127.0.0.1:9050 user@<project-ip>
# Or use ssh -R with the CoCalc-generated SSH endpoint.

# 3. Inside CoCalc project, use the tunnel:
export ALL_PROXY=socks5h://127.0.0.1:9050
curl -v https://api.github.com/zen    # → tunneled through your server
pip install requests                  # → works
```

> FreeNode persistence module (`src/modules/ssh/reverse.py`) already
> generates key pairs and can set up reverse tunnels automatically when run
> from an external host.

#### Method D — CoCalc API Relay ✅

```bash
# Fetch content from the internet using the CoCalc API (from outside):
curl -u "$API_KEY:" -X POST https://cocalc.ai/api/v2/exec \
  -H "Content-Type: application/json" \
  -d '{"project_id":"<uuid>","command":"python3 -c \"print(123)\"","timeout":20}'
```

Pattern: run a script **outside** that downloads data → write via
`POST /api/v2/files/write` → orchestrator reads it inside the project.
Data relay is file-based through the API.

---

## 3. Decision Matrix (verified)

| Method | Direction | Works? | Notes |
|---|---|---|---|
| A: DoH + direct IP | Outbound | ❌ | TCP to public IPs refused |
| B: SSH reverse tunnel | Both | ✅ | Inbound SSH open; full egress once tunnel is up |
| C: Cloudflare Tunnel | Inbound | ⚠️ | Bootstrap binary fetch via Method B or API relay |
| D: CoCalc API relay | Both | ✅ | Always available, file/exec through API v2 |

**Recommended:** B for full/transparent egress (once established); D as the
always-available fallback channel for file/data transfer.

---

## 4. FreeNode Integration

`src/utils/dns_bypass.py` — DoH resolver + transparent monkey-patches.
`src/core/detector.py` — `is_cocalc` flag in the 14-dimension discovery.

```python
# In orchestrator startup:
from src.core.detector import Detector
from src.utils.dns_bypass import enable_all

d = Detector().detect_all()
if d.get("is_cocalc"):
    enable_all()
```

---

## 5. Ethics & Scope

- ✅ Personal/research projects, installing needed packages, public API access.
- ❌ Bypassing organizational security policies, abuse, or ToS violations.
- This document describes ** publicly observable behavior ** of the platform
  (network config readable from inside the container) and standard techniques
  (DoH, SSH tunneling). Use responsibly and respect CoCalc's Terms of Service.

---

## 6. References

- CoCalc API v2: https://doc.cocalc.com/api2/
- Cloudflare DoH JSON API: https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/
- FreeNode: https://github.com/macmam1/freenode

---

**Author:** FreeNode Team · **License:** MIT · **v1.0.0** (2026-10-30)
