# FreeNode — Free Compute Platform Bypass

**Never let cloud platforms sleep your projects again.**

FreeNode is a complete framework for persistent, free compute on platforms like Render, Railway, Fly.io, Kaggle, Colab, and more — using intelligent deception, obfuscation, and automation.

---

## 🚀 Quick Start (One-liner)

```bash
curl -fsSL https://raw.githubusercontent.com/macmam1/freenode/main/install.sh | bash
```

Dashboard will start on `http://localhost:8080`

---

## ✨ Features

### 🎯 **Professional Dashboard**
- 💻 **Full Terminal** — xterm.js PTY over WebSocket
- 📁 **File Explorer** — Browse, edit, create, delete
- ⚙️ **Process Monitor** — Real-time CPU/Memory, kill processes
- 🛠️ **Settings Panel** — Live config management

### 🕵️ **Deception Layer**
- Masks as legitimate "svc-wrapper" service
- 56+ sensitive pattern scrubbing (ssh, tunnel, bypass, etc.)
- Platform-specific behavioral mimicry (health checks, metrics, logs)
- Process/network/filesystem identity spoofing

### 🔒 **Obfuscation Layer**
- XOR+Base85 string encryption (no plaintext at rest)
- Adaptive quiet mode (anti-analysis triggers)
- Artifact stripping (logs, timestamps, metadata)

### 🎛️ **CLI Control**
```bash
freenodectl status           # Show platform + modules
freenodectl enable ssh       # Enable SSH module
freenodectl deploy           # Run full deployment
freenodectl pack             # Encrypt + strip artifacts
freenodectl quiet            # Toggle quiet mode
```

---

## 📦 Installation

### Manual Install
```bash
git clone https://github.com/macmam1/freenode.git
cd freenode
pip install -r requirements.txt
python3 -m src.dashboard.app
```

### Platform-specific
```bash
# Render
curl -fsSL https://raw.githubusercontent.com/macmam1/freenode/main/install.sh | bash -s -- render

# Railway
curl -fsSL https://raw.githubusercontent.com/macmam1/freenode/main/install.sh | bash -s -- railway

# Generic
curl -fsSL https://raw.githubusercontent.com/macmam1/freenode/main/install.sh | bash
```

---

## 🏗️ Architecture

```
FreeNode v0.4.0
├── Core               Platform detection + orchestration
├── Deception          Identity masking (6 modules, 8 platforms)
├── Obfuscation        String encryption + anti-analysis
├── Dashboard          Professional UI + Terminal + API
└── Modules            SSH, Tunnel, Keepalive, API, Terminal
```

---

## 🎨 Dashboard Preview

- **Overview**: System stats + quick actions
- **Terminal**: Full shell access (xterm.js)
- **Files**: Project file management
- **Processes**: Monitor + kill capability
- **Settings**: Live configuration

Access: `http://localhost:8080`

---

## 🔧 Configuration

Edit `freenode.yaml`:

```yaml
platform: "auto"  # auto | render | railway | fly | kaggle | colab
dashboard_port: 8080

modules:
  ssh: "disabled"
  tunnel: "disabled"
  keepalive: "enabled"
  api: "enabled"

deception:
  log_scrub: true
  behavioral_mimicry: true
  string_encryption: true

obfuscation:
  quiet_mode: false
  artifact_strip: true
```

---

## 🛡️ Security

- **No credentials stored** — token-based auth only
- **Local root directory** — file access limited to project
- **Process isolation** — each deployment sandboxed
- **Obfuscated artifacts** — no plaintext identifiers

---

## 📚 Documentation

- [Installation Guide](docs/INSTALL.md) *(coming soon)*
- [Platform Support](docs/PLATFORMS.md) *(coming soon)*
- [API Reference](docs/API.md) *(coming soon)*

---

## 🤝 Contributing

This is a personal research project. Contributions welcome via issues/PRs.

---

## ⚖️ Legal

FreeNode is for **educational and personal use** on platforms you have legitimate access to. Respect platform ToS. The authors are not responsible for misuse.

---

## 📊 Status

| Component | Version | Status |
|-----------|---------|--------|
| Core | v0.0.2 | ✅ Stable |
| Deception | v0.1.0 | ✅ Stable |
| Obfuscation | v0.2.0 | ✅ Stable |
| Integration | v0.3.0 | ✅ Stable |
| Dashboard | v0.4.0 | ✅ Stable |

---

**Built with ❤️ for free compute enthusiasts**

