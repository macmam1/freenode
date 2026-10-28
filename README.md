# FreeNode — Universal Platform Bypass Framework

**Version:** 1.0.0 (MVP)  
**Author:** macmam1  
**License:** MIT  
**Status:** Active Development

---

## 🎯 What is FreeNode?

FreeNode is a **modular, self-contained framework** that:

1. **Detects** your platform environment (14 dimensions)
2. **Analyzes** limitations (sleep, session timeout, resource limits, etc.)
3. **Selects** the best strategy (keepalive, tunnel, persistence, API)
4. **Activates** modules automatically
5. **Archives** test results to GitHub

**Supported Platforms:** 80+ (Render, Railway, Colab, Kaggle, Cloudflare Workers, Vercel, and more)

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/macmam1/freenode.git
cd freenode
pip install -r requirements.txt
```

### Initialize

```bash
python cli.py diagnose    # See your platform profile
python cli.py init        # Setup for your environment
python cli.py start       # Activate all modules
```

### Check Status

```bash
python cli.py status      # View current modules
```

---

## 🏗️ Architecture

### Core (Detection + Strategy)

| Component | Purpose |
|---|---|
| **Detector** | Scans 14 environment dimensions (OS, RAM, CPU, platform, etc.) |
| **Profiler** | Maps limitations to a platform class |
| **Orchestrator** | Selects modules based on platform class |
| **Monitor** | Auto-revives failed modules |
| **Persistence** | Backups state to GitHub/Drive/S3 |

### Modules (Capabilities)

| Module | Purpose | Platforms |
|---|---|---|
| **keepalive** | Anti-sleep via HTTP ping / traffic generation | Render, Railway, Glitch, Colab |
| **terminal** | Web terminal (sshx, ttyd, gotty) | All |
| **tunnel** | External access (Cloudflare, sshx, frp, ngrok) | All |
| **ssh** | SSH server + key management | All |
| **api** | HTTP API for remote execution | All |
| **resource** | Bypass cgroup/RAM/CPU limits | Container platforms |
| **privilege** | Privilege escalation attempts | All |
| **persistence** | Backup to GitHub/Drive/S3 | All |

---

## 📊 Platform Coverage

### Containerized (Sleep-Limited)
- Render Free (15 min sleep)
- Railway Starter ($5 credit)
- Fly.io Free (256MB RAM)
- Glitch (5 min idle)
- Koyeb (no time limit)
- SnapDeploy (15 min sleep)
- Replit (Core $25/mo)
- And 20+ more...

### Notebook / GPU
- Google Colab (12h session)
- Kaggle Notebooks (30h/week)
- Molab.marimo.io
- Deepnote, Datalore
- Paperspace Gradient
- And 5+ more...

### Serverless / Edge
- Vercel (15s timeout)
- Netlify (15s timeout)
- Cloudflare Workers (always-on)
- Firebase, Supabase, Deno Deploy
- And 5+ more...

### Real VMs / SaaS
- Oracle Cloud Free (always-on)
- Google Cloud, AWS, Azure
- Belmo, Stormkit, Zeabur
- And 40+ more...

---

## 🧪 Testing & Results

Every platform test is automatically:
1. ✅ Executed with strategy validation
2. 📝 Documented in `docs/test-registry/`
3. 🏷️ Tagged in Git for retrieval
4. 📦 Archived permanently (never deleted)

### Test Status

| Platform | Status | Result | Date |
|---|---|---|---|
| Render | ⏳ Pending | — | — |
| Railway | ⏳ Pending | — | — |
| Colab | ⏳ Pending | — | — |
| Kaggle | ⏳ Pending | — | — |
| Cloudflare | ⏳ Pending | — | — |

*(See `docs/test-registry/` for detailed results)*

---

## 📖 Documentation

- **Architecture:** See `docs/ANALYSIS_PART1.md`, `docs/ANALYSIS_PART2.md`, `docs/ANALYSIS_PART3.md`
- **Usage Guide:** Run `python cli.py --help`
- **Test Results:** Check `docs/test-registry/`

---

## 🛠️ Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black src/
flake8 src/
```

### Add New Platform

1. Add platform detection logic to `src/core/detector.py`
2. Create strategy in `src/core/profiler.py`
3. Test and document in `docs/test-registry/`

---

## 📋 Features (MVP)

- ✅ 14-dimension environment detection
- ✅ 80+ platform support mapping
- ✅ Modular architecture (pick what you need)
- ✅ Auto-strategy selection
- ✅ Persistent state backup
- ✅ CLI interface
- ✅ HTTP API
- ⏳ Full tunnel chain (Cloudflare → sshx → frp → ngrok)
- ⏳ Session keepalive (5 strategies)
- ⏳ Web terminal integration
- ⏳ Resource limit bypass

---

## 🔒 Security Notes

- FreeNode does **not** expose secrets in logs
- All platform tokens are masked
- State is backed up encrypted (when available)
- No telemetry or external reporting

---

## 🤝 Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines.

---

## 📞 Support

- Issues: [GitHub Issues](https://github.com/macmam1/freenode/issues)
- Discussions: [GitHub Discussions](https://github.com/macmam1/freenode/discussions)

---

## 📜 License

MIT License — See `LICENSE` file for details.

---

## 🎉 Acknowledgments

Built on research from 50+ open-source projects and 12 internal repositories. Special thanks to the communities behind:
- Cloudflare Tunnel
- sshx.io
- frp
- Proot
- And many others

---

**Status:** 🚀 **Active Development** — MVP phase (v1.0.0)  
**Last Updated:** 2026-10-28  
**Next Milestone:** Full module implementation + platform testing
