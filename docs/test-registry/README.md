# Test Registry — FreeNode Platform Validation

> **قانون طلایی:** هر تست در این پوشه بایگانی می‌شود و **هرگز حذف نمی‌شود**. هر تست یک commit و یک tag جداگانه دارد.

---

## 📋 فرمت نتیجه تست

هر فایل تست باید شامل این فیلدها باشد:

| فیلد | توضیح |
|---|---|
| `test_id` | شناسه یکتا (مثلاً `render-001`) |
| `date` | تاریخ انجام تست |
| `version` | نسخهٔ FreeNode |
| `platform` | نام پلتفرم |
| `url` | لینک پلتفرم |
| `environment` | نوع محیط |
| `limitations_found` | محدودیت‌های کشف‌شده |
| `modules_attempted` | ماژول‌های تلاش‌شده |
| `modules_successful` | ماژول‌های موفق |
| `modules_failed` | ماژول‌های شکست‌خورده |
| `tunnel_status` | وضعیت تونل |
| `endpoint` | URL دسترسی خارجی |
| `notes` | یادداشت‌های مهم |
| `next_steps` | قدم‌های بعدی |

---

## 📅 Test Status Dashboard

### Phase 1: Containerized Platforms
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 1 | Render Free | ⏳ pending | — | — | `render-2026-XX-XX.md` |
| 2 | Railway Starter | ⏳ Pending | — | — | `railway-2026-XX-XX.md` |
| 3 | Koyeb Free | ⏳ Pending | — | — | `koyeb-2026-XX-XX.md` |
| 4 | Fly.io Free | ⏳ Pending | — | — | `flyio-2026-XX-XX.md` |
| 5 | Glitch | ⏳ Pending | — | — | `glitch-2026-XX-XX.md` |
| 6 | SnapDeploy | ⏳ Pending | — | — | `snapdeploy-2026-XX-XX.md` |
| 7 | Freestyle.sh | ⏳ Pending | — | — | `freestyle-2026-XX-XX.md` |
| 8 | Runloop.ai | ⏳ Pending | — | — | `runloop-2026-XX-XX.md` |

### Phase 2: Notebook Platforms
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 9 | Google Colab | ⏳ Pending | — | — | `colab-2026-XX-XX.md` |
| 10 | Kaggle Notebooks | ⏳ Pending | — | — | `kaggle-2026-XX-XX.md` |
| 11 | Molab.marimo.io | ⏳ Pending | — | — | `molab-2026-XX-XX.md` |
| 12 | Deepnote | ⏳ Pending | — | — | `deepnote-2026-XX-XX.md` |
| 13 | Datalore | ⏳ Pending | — | — | `datalore-2026-XX-XX.md` |

### Phase 2: Serverless / Edge
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 14 | Cloudflare Workers | ⏳ Pending | — | — | `cloudflare-2026-XX-XX.md` |
| 15 | Vercel | ⏳ Pending | — | — | `vercel-2026-XX-XX.md` |
| 16 | Netlify | ⏳ Pending | — | — | `netlify-2026-XX-XX.md` |
| 17 | Deno Deploy | ⏳ Pending | — | — | `deno-2026-XX-XX.md` |
| 18 | Supabase | ⏳ Pending | — | — | `supabase-2026-XX-XX.md` |
| 19 | Firebase | ⏳ Pending | — | — | `firebase-2026-XX-XX.md` |

### Phase 3: Real VM / SaaS
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 20 | Oracle Cloud Free | ⏳ Pending | — | — | `oracle-2026-XX-XX.md` |
| 21 | Belmo.io | ⏳ Pending | — | — | `belmo-2026-XX-XX.md` |
| 22 | Stormkit.io | ⏳ Pending | — | — | `stormkit-2026-XX-XX.md` |
| 23 | Zeabur.com | ⏳ Pending | — | — | `zeabur-2026-XX-XX.md` |
| 24 | Qoddi.com | ⏳ Pending | — | — | `qoddi-2026-XX-XX.md` |
| 25 | Encore.dev | ⏳ Pending | — | — | `encore-2026-XX-XX.md` |
| 26 | AlwaysData | ⏳ Pending | — | — | `alwaysdata-2026-XX-XX.md` |
| 27 | HelioHost | ⏳ Pending | — | — | `heliohost-2026-XX-XX.md` |

### Phase 3: Micro-VM / Sandbox
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 28 | GitHub Codespaces | ⏳ Pending | — | — | `codespaces-2026-XX-XX.md` |
| 29 | Gitpod | ⏳ Pending | — | — | `gitpod-2026-XX-XX.md` |
| 30 | Stackblitz | ⏳ Pending | — | — | `stackblitz-2026-XX-XX.md` |
| 31 | CodeSandbox | ⏳ Pending | — | — | `codesandbox-2026-XX-XX.md` |
| 32 | E2B | ⏳ Pending | — | — | `e2b-2026-XX-XX.md` |
| 33 | Daytona.io | ⏳ Pending | — | — | `daytona-2026-XX-XX.md` |

### Phase 3: CI/CD
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 34 | GitHub Actions | ⏳ Pending | — | — | `github-actions-2026-XX-XX.md` |
| 35 | GitLab CI | ⏳ Pending | — | — | `gitlab-ci-2026-XX-XX.md` |
| 36 | CircleCI | ⏳ Pending | — | — | `circleci-2026-XX-XX.md` |
| 37 | Buddy.works | ⏳ Pending | — | — | `buddy-2026-XX-XX.md` |
| 38 | Buildkite | ⏳ Pending | — | — | `buildkite-2026-XX-XX.md` |
| 39 | Semaphore | ⏳ Pending | — | — | `semaphore-2026-XX-XX.md` |
| 40 | Appcircle.io | ⏳ Pending | — | — | `appcircle-2026-XX-XX.md` |

### Phase 3: MLOps / Data
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 41 | HuggingFace Spaces | ⏳ Pending | — | — | `huggingface-2026-XX-XX.md` |
| 42 | Hopsworks.ai | ⏳ Pending | — | — | `hopsworks-2026-XX-XX.md` |
| 43 | ClearML | ⏳ Pending | — | — | `clearml-2026-XX-XX.md` |
| 44 | Pulumi | ⏳ Pending | — | — | `pulumi-2026-XX-XX.md` |

### Phase 4: Static / Other
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 45 | PythonAnywhere | ⏳ Pending | — | — | `pythonanywhere-2026-XX-XX.md` |
| 46 | InfinityFree | ⏳ Pending | — | — | `infinityfree-2026-XX-XX.md` |
| 47 | AwardSpace | ⏳ Pending | — | — | `awardspace-2026-XX-XX.md` |
| 48 | Val.town | ⏳ Pending | — | — | `val-town-2026-XX-XX.md` |
| 49 | Codeberg | ⏳ Pending | — | — | `codeberg-2026-XX-XX.md` |
| 50 | Tiiny.host | ⏳ Pending | — | — | `tiiny-2026-XX-XX.md` |

### Phase 5: Remaining Platforms (30+)
| # | Platform | Status | Result | Date | File |
|---|---|---|---|---|---|
| 51 | AlwaysData | ⏳ Pending | — | — | `alwaysdata-2026-XX-XX.md` |
| 52 | Appwrite | ⏳ Pending | — | — | `appwrite-2026-XX-XX.md` |
| 53 | Back4App | ⏳ Pending | — | — | `back4app-2026-XX-XX.md` |
| 54 | Nhost | ⏳ Pending | — | — | `nhost-2026-XX-XX.md` |
| 55 | 8base | ⏳ Pending | — | — | `8base-2026-XX-XX.md` |
| 56 | Ninox | ⏳ Pending | — | — | `ninox-2026-XX-XX.md` |
| 57 | Pulumi | ⏳ Pending | — | — | `pulumi-2026-XX-XX.md` |
| 58 | Aiven | ⏳ Pending | — | — | `aiven-2026-XX-XX.md` |
| 59 | Cockroach Labs | ⏳ Pending | — | — | `cockroachlabs-2026-XX-XX.md` |
| 60 | Clever Cloud | ⏳ Pending | — | — | `clever-2026-XX-XX.md` |
| 61 | ClearML | ⏳ Pending | — | — | `clear-2026-XX-XX.md` |
| 62 | Hopsworks.ai | ⏳ Pending | — | — | `hopsworks-2026-XX-XX.md` |
| 63 | Runkoda | ⏳ Pending | — | — | `runkoda-2026-XX-XX.md` |
| 64 | OpenShip.io | ⏳ Pending | — | — | `openship-2026-XX-XX.md` |
| 65 | VibeNest | ⏳ Pending | — | — | `vibenest-2026-XX-XX.md` |
| 66 | BotKeep.cloud | ⏳ Pending | — | — | `botkeep-2026-XX-XX.md` |
| 67 | LiveMy.app | ⏳ Pending | — | — | `livemy-2026-XX-XX.md` |
| 68 | Superserve.ai | ⏳ Pending | — | — | `superserve-2026-XX-XX.md` |
| 69 | Katabump | ⏳ Pending | — | — | `katabump-2026-XX-XX.md` |
| 70 | Cloud.dada-tuda.ru | ⏳ Pending | — | — | `dada-tuda-2026-XX-XX.md` |
| 71 | Open.claw.cloud | ⏳ Pending | — | — | `open-claw-2026-XX-XX.md` |
| 72 | Prepare.sh | ⏳ Pending | — | — | `prepare-2026-XX-XX.md` |
| 73 | Hopx.ai | ⏳ Pending | — | — | `hopx-2026-XX-XX.md` |
| 74 | RDPhostings.com | ⏳ Pending | — | — | `rdphostings-2026-XX-XX.md` |
| 75 | Kubeletto.com | ⏳ Pending | — | — | `kubeletto-2026-XX-XX.md` |
| 76 | Wispbyte.com | ⏳ Pending | — | — | `wispbyte-2026-XX-XX.md` |
| 77 | Serverix.cloud | ⏳ Pending | — | — | `serverix-2026-XX-XX.md` |
| 78 | Atyro.cloud | ⏳ Pending | — | — | `atyro-2026-XX-XX.md` |
| 79 | Lucity.cloud | ⏳ Pending | — | — | `lucity-2026-XX-XX.md` |
| 80 | Pella.app | ⏳ Pending | — | — | `pella-2026-XX-XX.md` |
| 81 | Superserve.ai | ⏳ Pending | — | — | `superserve-2026-XX-XX.md` |
| 82 | Labs.2z2.top | ⏳ Pending | — | — | `labs-2z2-2026-XX-XX.md` |
| 83 | ChainIde.com | ⏳ Pending | — | — | `chainide-2026-XX-XX.md` |
| 84 | VibeNest.net | ⏳ Pending | — | — | `vibenest-2026-XX-XX.md` |
| 85 | Openship.io | ⏳ Pending | — | — | `openship-2026-XX-XX.md` |
| 86 | BotKeep.cloud | ⏳ Pending | — | — | `botkeep-2026-XX-XX.md` |
| 87 | LiveMy.app | ⏳ Pending | — | — | `livemy-2026-XX-XX.md` |
| 88 | Deno Deploy | ⏳ Pending | — | — | `deno-2026-XX-XX.md` |
| 89 | Wasmer.io | ⏳ Pending | — | — | `wasmer-2026-XX-XX.md` |
| 90 | Fleek.sh | ⏳ Pending | — | — | `fleek-2026-XX-XX.md` |
| 91 | Boxd.sh | ⏳ Pending | — | — | `boxd-2026-XX-XX.md` |
| 92 | Val.town | ⏳ Pending | — | — | `val-town-2026-XX-XX.md` |
| 93 | Codeberg.org | ⏳ Pending | — | — | `codeberg-2026-XX-XX.md` |
| 94 | Stackblitz | ⏳ Pending | — | — | `stackblitz-2026-XX-XX.md` |
| 95 | CodeSandbox | ⏳ Pending | — | — | `codesandbox-2026-XX-XX.md` |
| 96 | Buddy.works | ⏳ Pending | — | — | `buddy-2026-XX-XX.md` |
| 97 | Buildkite | ⏳ Pending | — | — | `buildkite-2026-XX-XX.md` |
| 98 | Semaphore | ⏳ Pending | — | — | `semaphore-2026-XX-XX.md` |
| 99 | Appcircle.io | ⏳ Pending | — | — | `appcircle-2026-XX-XX.md` |
| 100 | Kinsta | ⏳ Pending | — | — | `kinsta-2026-XX-XX.md` |

---

## 📝 Template for Test Results

```markdown
# [Platform Name] Test Result — YYYY-MM-DD

## Test Details
- **test_id:** `platform-001`
- **date:** `YYYY-MM-DD`
- **version:** `v1.0.0`
- **platform:** Platform Name
- **url:** https://platform-url.com
- **environment:** Containerized / Notebook / Serverless / VM / SaaS

## Limitations Found
- [ ] sleep_minutes: 15
- [ ] session_hours: 12
- [ ] ram_gb: 0.5
- [ ] disk_gb: 3

## Modules Tested
| Module | Status | Notes |
|---|---|---|
| keepalive | ✅ / ❌ | — |
| tunnel | ✅ / ❌ | — |
| ssh | ✅ / ❌ | — |
| api | ✅ / ❌ | — |

## Results
- **Overall Status:** PASS / FAIL / PARTIAL
- **External Access:** URL or "failed"
- **Notes:** ...

## Next Steps
- [ ] Try alternative tunnel
- [ ] Improve keepalive strategy
```

---

## 🏷️ Tagging Convention

Every test commit must be tagged:
- `test-render-2026-10-30`
- `test-colab-2026-11-05`
- `test-cloudflare-2026-11-12`

---

## 📦 Archive Policy

- ✅ Old test files are **never deleted**
- ✅ Each test has its own commit
- ✅ Each test has a Git tag
- ✅ Results archived in `docs/test-registry/archive/` when versioned
- ✅ JSON logs kept in `tests/results/`

---

**Last Updated:** 2026-10-28  
**Registry Maintainer:** macmam1 + FreeNode AI Agents
