# Agent-nodii Research — Part 3: Module Strategy Matrix + Test Registry

## 🎯 هدف مهندسی

یک برنامهٔ **self-contained** بنویسیم که روی هر پلتفرمی نصب می‌شود، محدودیت‌ها را تشخیص می‌دهد، ماژول مناسب را فعال می‌کند، و همهٔ فعالیت‌ها به‌صورت **کامیل و versioned** در یک مخزن GitHub مستند می‌شوند.

---

## 👷‍♂️ معماری ماژولار (v3 — پرداخت‌پذیر / Modular)

```
agent-nodii/
├── cli.py                              # نقطهٔ ورود (single binary)
├── core/
│   ├── detector.py                     # 14-dimension محیط کشف
│   ├── profiler.py                     # تولید پروفایل (limitations summary)
│   ├── stratifier.py                   # دسته‌بندی پلتفرم (Platform class)
│   ├── orchestrator.py                 # ترکیب ماژول‌ها (strategy selector)
│   ├── monitor.py                      # نظارت + auto-revive
│   └── persistence.py                  # backup state to external (GitHub/Drive/S3)
│
├── modules/
│   ├── keepalive/
│   │   ├── http_ping.py                # ping health endpoint every 10 mins
│   │   ├── traffic_gen.py              # generate HTTP traffic to self
│   │   ├── browser_sim.py              # simulate browser tab open
│   │   └── scheduler.py                # cron-based wake-up
│   │
│   ├── terminal/
│   │   ├── web.py                      # build-in web terminal (FastAPI + xterm.js)
│   │   ├── sshx.py                     # sshx.io auto-deploy
│   │   ├── ttyd.py                     # ttyd fallback
│   │   └── gotty.py                    # gotty fallback
│   │
│   ├── tunnel/
│   │   ├── cloudflare.py               # cloudflared tunnel wrapper
│   │   ├── sshx.py                     # sshx reverse tunnel
│   │   ├── frp.py                      # frp client auto-config
│   │   ├── ngrok.py                    # ngrok auto-start
│   │   └── localtunnel.py              # localtunnel fallback
│   │
│   ├── ssh/
│   │   ├── sshd.py                     # install/run sshd (or dropbear)
│   │   ├── key_manager.py              # SSH key lifecycle
│   │   └── reverse.py                  # reverse SSH tunnel to external
│   │
│   ├── resource/
│   │   ├── cgroup_bypass.py            # cgroup manipulation (freeroot)
│   │   ├── memory_opt.py               # RAM cleanup + swap
│   │   ├── disk_quota.py               # bypass disk quota (AlwaysData)
│   │   └── proot.py                    # fake root environment
│   │
│   ├── privilege/
│   │   ├── escalate.py                 # try sudo/root escalation
│   │   └── persistence.py              # cron / systemdless
│   │
│   ├── token/
│   │   ├── api_capture.py              # capture platform API tokens
│   │   ├── auth_bypass.py              # bypass platform auth
│   │   └── refresh_manager.py          # manage token refresh
│   │
│   └── api/
│       ├── server.py                   # HTTP API (exec/files/env)
│       ├── auth.py                     # auth middleware
│       └── commands.py                 # command endpoints
│
├── profiles/
│   └── platform_strategies.json        # platform → module mapping
│
├── tests/
│   ├── platform/                        # per-platform tests
│   │   ├── render/
│   │   ├── railway/
│   │   ├── colap/
│   │   ├── ...
│   └── results/                         # test results (archived in git)
│
├── docs/
│   ├── architecture.md
│   ├── usage.md
│   └── test-registry/                    # test results archive
│       ├── 2026-10-28_render_v0.1.md
│       ├── 2026-11-02_railway_v0.1.md
│       └── ...
│
├── .github/workflows/
│   ├── ci.yml                          # lint + unit tests
│   └── archive_results.yml             # auto-archive test results to git
│
├── requirements.txt
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🧪 استراتژی ماژولی برای هر کلاس پلتفرم

| Platform Class | Modules Needed | Modules Skip | Default Tunnel | Keepalive Strategy |
|---|---|---|---|---|
| **Containerized Free** | keepalive, tunnel, api | privilege, proot | sshx → cloudflare → ngrok | http_ping + traffic_gen |
| **SaaS / Always-On** | tunnel, api | keepalive, privilege | cloudflare | none |
| **Notebook / VM** | keepalive, terminal, ssh, persistence | proot | sshx → frp | browser_sim + scheduler |
| **Serverless / Edge** | api, tunnel (relay) | keepalive, ssh | — | external relay |
| **Static Only** | tunnel (relay) | all local | external proxy | — |

---

## 🧪 رجیستری تست‌ها (Test Registry)

**قانون طلایی:** هر تست در یک پوشه مخصوص خودش نگهداری می‌شود؛ نتایج در `docs/test-registry/` بایگانی می‌شوند؛ هیچ فایل قدیمی حذف نمی‌شود.

### 📋 فرمت نتیجه تست

هر تست حداقل شامل این فیلدها می‌شود:

| فیلد | توضیح | مثال |
|---|---|---|
| test_id | شناسه یکتا | `render-free-001` |
| date | تاریخ انجام تست | `2026-10-28` |
| version | نسخهٔ FreeNode | `v0.3.1` |
| platform | نام پلتفرم | `Render Free` |
| url | لینک پلتفرم | `https://render.com` |
| environment | نوع محیطی | `Containerized` |
| limitations_found | محدودیت‌های کشف شده | `["idle_15m", "ram_512MB"]` |
| modules_attempted | ماژول‌هایی که سعی شد | `["keepalive", "sshx", "cloudflare"]` |
| modules_successful | ماژول‌های موفق | `["keepalive", "sshx"]` |
| modules_failed | ماژول‌های شکست‌خورده | `["cloudflare"]` |
| tunnel_status | آیا تونل کار می‌کند؟ | `active` |
| endpoint | URL دسترسی خارجی | `https://abc123.sshx.io` |
| notes | یادداشت‌های مهم | `cloudflared can not auth` |
| next_steps | قدم‌های بعدی | `try frp instead` |

---

## 🗺️ جدول استراتژی ماژولی (در حال بروز رسانی)

| # | Platform | Class | Keepalive | Tunnel 1 | Tunnel 2 | Tunnel 3 | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Render | Containerized | http_ping | sshx | cloudflare | ngrok | sleep after 15min |
| 2 | Railway | Containerized | traffic_gen | sshx | frp | — | $5 credit limit |
| 3 | Koyeb | Always-On | none | cloudflare | sshx | — | no sleep |
| 4 | Fly.io | Containerized | http_ping | sshx | cloudflare | — | 256MB RAM |
| 5 | Glitch | Containerized | traffic_gen | sshx | localtunnel | — | 5min idle |
| 6 | Replit | Containerized | browser_sim | sshx | ngrok | — | Core $25/mo |
| 7 | Colab | Notebook | scheduler | sshx | cloudflare | — | 12h session |
| 8 | Kaggle | Notebook | scheduler | sshx | frp | — | 30h/week |
| 9 | Molab | Notebook | scheduler | sshx | — | — | kernel dies |
| 10 | Vercel | Serverless | — | — | — | — | 15s timeout |
| 11 | Netlify | Serverless | — | — | — | — | 15s timeout |
| 12 | Cloudflare Workers | Edge | — | — | — | — | KV relay |
| 13 | Oracle Cloud | VM | none | direct | — | — | always-on |
| 14 | GitHub Codespaces | Sandbox | scheduler | sshx | — | — | 60h/month |
| 15 | HuggingFace | Notebook/SaaS | scheduler | cloudflare | — | — | always-on |
| 16 | Supabase | SaaS | none | direct | — | — | real backend |
| 17 | Firebase | Serverless | — | — | — | — | 15s timeout |
| 18 | Deno Deploy | Edge | — | — | — | — | 15s timeout |
| 19 | Belmo | SaaS | none | direct | — | — | always-on |
| 20 | Stormkit | SaaS | none | direct | — | — | always-on |
| 21 | AlwaysData | SaaS | none | sshx | cloudflare | — | 1GB disk limit |
| 22 | Gitpod | Sandbox | scheduler | sshx | — | — | 500h/month |
| 23 | Deepnote | Notebook | scheduler | sshx | — | — | session-based |
| 24 | Datalore | Notebook | scheduler | sshx | — | — | session-based |
| 25 | Stackblitz | Static | — | — | — | — | browser-only |
| 26 | CodeSandbox | Static | — | — | — | — | browser-only |
| 27 | Freestyle.sh | Containerized | traffic_gen | sshx | frp | — | deploy-only |
| 28 | Runloop.ai | Container | traffic_gen | sshx | cloudflare | — | ephemeral |
| 29 | Clever Cloud | Containerized | http_ping | sshx | frp | — | free dev plan |
| 30 | HelioHost | SaaS | none | direct | — | — | real shared server |
| 31 | SnapDeploy | Containerized | traffic_gen | sshx | localtunnel | — | 15min sleep |
| 32 | AwardSpace | Static | — | — | — | — | 100MB disk |
| 33 | InfinityFree | Static | — | — | — | — | web hosting only |
| 34 | Wasmer.io | Edge | — | — | — | — | WASM runtime |
| 35 | Fleek.sh | Static | — | — | — | — | decentralized |
| 36 | Supabase | SaaS | none | direct | — | — | real backend |
| 37 | Appwrite | SaaS | none | direct | — | — | self-hosted BaaS |
| 38 | Nhost | SaaS | none | direct | — | — | GraphQL BaaS |
| 39 | 8base | SaaS | none | direct | — | — | GraphQL BaaS |
| 40 | Back4App | SaaS | none | direct | — | — | GraphQL BaaS |
| 41 | Ninox | SaaS | none | direct | — | — | database BaaS |
| 42 | Pulumi | DevOps | — | — | — | — | IaC tool |
| 43 | HuggingFace | Notebook/SaaS | scheduler | cloudflare | — | — | always-on |
| 44 | Hopsworks.ai | MLOps | scheduler | sshx | frp | — | resource limited |
| 45 | Boxd.sh | Static | — | — | — | — | بررسی نشده |
| 46 | Val.town | Serverless | — | — | — | — | scripting-only |
| 47 | Codeberg | Static | — | — | — | — | git hosting |
| 48 | Buddy.works | CI/CD | scheduler | sshx | — | — | ۵۰۰ دقیقه/ماه |
| 49 | Buildkite | CI/CD | scheduler | sshx | — | — | ۳۰ دقیقه/جاب |
| 50 | Semaphore | CI/CD | scheduler | sshx | — | — | ۸۵۰ دقیقه/ماه |
| 51 | Appcircle.io | CI/CD | scheduler | sshx | — | — | ۱۰۰ بیلد/ماه |
| 52 | GitHub Actions | CI/CD | scheduler | sshx | — | — | ۲۴۰۰ دقیقه/ماه |
| 53 | Cloud.dada-tuda.ru | VM | none | direct | — | — | روسیه، ۵۱۲MB |
| 54 | Datadog | Static | — | — | — | — | بررسی نشده |
| 55 | Grafana | SaaS | none | direct | — | — | free tier |
| 56 | Runkoda | SaaS | none | direct | — | — | بررسی نشده |
| 57 | Labs.2z2.top | VM | none | direct | — | — | ۱ ساعت/روز |
| 58 | Chainide | Sandbox | traffic_gen | sshx | cloudflare | — | needs keepalive |
| 59 | Open.claw.cloud | VM | none | direct | — | — | بررسی نشده |
| 60 | Katabump | SaaS | none | direct | — | — | بررسی نشده |
| 61 | Hopx.ai | VM | none | direct | — | — | بررسی نشده |
| 62 | Prepare.sh | DevOps | — | — | — | — | بررسی نشده |
| 63 | Botkeep.cloud | SaaS | none | direct | — | — | بررسی نشده |
| 64 | Livemy.app | SaaS | none | direct | — | — | بررسی نشده |
| 65 | Dayta.io | VM | none | direct | — | — | بررسی نشده |
| 66 | Vibenest | SaaS | none | direct | — | — | بررسی نشده |
| 67 | Openship.io | DevOps | scheduler | sshx | — | — | بررسی نشده |
| 68 | Kinsta.com | SaaS | none | direct | — | — | free dev tier |
| 69 | Encore.dev | SaaS | none | direct | — | — | always-on |
| 70 | Apply.build | SaaS | none | direct | — | — | always-on |
| 71 | Tiiny.host | SaaS | none | direct | — | — | always-on |
| 72 | Qoddi.com | SaaS | none | direct | — | — | always-on |
| 73 | Serverix.cloud | Containerized | http_ping | sshx | frp | — | resource limited |
| 74 | Atyro.cloud | VM | none | direct | — | — | بررسی نشده |
| 75 | Lucity.cloud | VM | none | direct | — | — | بررسی نشده |
| 76 | Pella.app | SaaS | none | direct | — | — | بررسی نشده |
| 77 | Superserve.ai | SaaS | none | direct | — | — | بررسی نشده |
| 78 | Aiven.io | SaaS | none | direct | — | — | managed DB |
| 79 | CockroachLabs | SaaS | none | direct | — | — | managed DB |
| 80 | IBM Cloud Free | VM | none | direct | — | — | ۲۵ کلاس compute |

---

## 🧪 برنامهٔ تست (Testing Plan)

### فاز 1: Containerized Free Platforms
| # | پلتفرم | تاریخ | وضعیت | لینک نتیجه |
|---|---|---|---|---|
| 1 | Render | 2026-10-30 | ✴ pending | docs/test-registry/render-2026-10-30.md |
| 2 | Railway | 2026-10-31 | ✴ pending | docs/test-registry/railway-2026-10-31.md |
| 3 | Glide (Glitch) | 2026-11-02 | ✴ pending | docs/test-registry/glitch-2026-11-02.md |

### فاز 2: Notebook / VM Platforms
| # | پلتفرم | تاریخ | وضعیت | لینک نتیجه |
|---|---|---|---|---|
| 4 | Google Colab | 2026-11-05 | ✴ pending | docs/test-registry/colab-2026-11-05.md |
| 5 | Kaggle | 2026-11-07 | ✴ pending | docs/test-registry/kaggle-2026-11-07.md |

### فاز 3: Serverless / Edge
| # | پلتفرم | تاریخ | وضعیت | لینک نتیجه |
|---|---|---|---|---|
| 6 | Cloudflare Workers | 2026-11-10 | ✴ pending | docs/test-registry/cloudflare-2026-11-10.md |
| 7 | Vercel | 2026-11-12 | ✴ pending | docs/test-registry/vercel-2026-11-12.md |

*(ادامه در ISSUE #1 در GitHub)*

---

## 📦 استراتژی بایگانی

1. هر تست در `docs/test-registry/` یک فایل مارک‌داون دارد
2. فایل‌های قبلی **هرگز حذف نمی‌شوند**
3. هر تست یک **commit** جداگانه در GitHub دارد
4. هر تست یک **label** GitHub دارد (مثلا `test-passed`, `test-failed`)
5. فایل‌های قبلی در `docs/test-registry/archive/` بایگانی می‌شوند

**قالب نام فایل:** `platform-version-date.md`  
**مثال:** `render-v0.3.0-2026-10-30.md`

---

## ⚙️ ابزارهای مورد نیاز برای تست

| ماژول | وابستگی | نصب در Docker | نکات |
|---|---|---|---|
| keepalive | Python 3.x, requests, selenium | ✅ | نیاز به مرورگر برای browser_sim |
| terminal | FastAPI, xterm.js | ✅ | — |
| tunnel | cloudflared, sshx CLI, frp, ngrok | ✅ | برای cloudflare نیاز به token |
| ssh | dropbear, openssh | ✅ | — |
| resource | proot, cgroup tools | ✅ | نیاز به kernel features |
| api | FastAPI, uvicorn | ✅ | — |
| persistence | git, github cli | ✅ | نیاز به token |

---

## 🪝 اسکریپت خودکار بایگانی تست

```bash
#!/bin/bash
# auto-archive-test.sh

PLATFORM=$1
VERSION="v$(grep version pyproject.toml | cut -d'"' -f2)"
DATE=$(date +%Y-%m-%d)
RESULT_FILE="docs/test-registry/${PLATFORM}-${VERSION}-${DATE}.md"

# Run test
python -m agent_nodii.cli test-platform $PLATFORM

# Create result file
cat > $RESULT_FILE << EOF
# ${PLATFORM} Test Result — ${DATE}

## Result Details
- test_id: ${PLATFORM}-${VERSION}-${DATE}
- date: ${DATE}
- version: ${VERSION}
... (auto-generated from test output)
EOF

# Commit
git add $RESULT_FILE
git commit -m "test:${PLATFORM} ${VERSION} ${DATE}"
git tag "test-${PLATFORM}-${DATE}"
git push origin main --tags

echo "✅ Results for ${PLATFORM} archived at ${RESULT_FILE}"
```

---

## 📊 خروجی نهایی هر تست (برای GitHub)

هر تست باید خروجی زیر را تولید کند:

1. **یک فایل Markdown** در `docs/test-registry/` شامل:
   - نتایج آزمون‌ها
   - ماژول‌های موفق/ناموفق
   - لینک دسترسی خارجی (اگر موفق باشد)
   - یادداشت مهم
2. **یک لاگ JSON** در `tests/results/` شامل:
   - تمام داده‌های دقیق از تست
3. **یک برچسب (tag)** در گیت:
   - `test-<platform>-<date>`
4. **یک آرشیو ZIP** در `tests/results/archive/` شامل:
   - تمام فایل‌ها و لاگ‌ها

این اطلاعات تکمیل می‌شوند تا ماژول‌های بعدی بتوانند همه تجربیات قبلی را بازنگری کنند.

---

**برای مشاهدهٔ تمام پلتفرم‌ها و استراتژی‌های کامل، به `agent-nodii-research/ANALYSIS_PART2.md` مراجعه کنید.**