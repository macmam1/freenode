# Agent-nodii Research — Part 2: Refined Taxonomy + Platform Strategies

## 📊 کلاس‌بندی نهایی ۷۳ پلتفرم

---

### 1️⃣ **Containerized Free Platforms**  
**ویژگی:** واقعاً VM یا container؛ معمولاً sleep یا محدودیت منابع دارد  

| # | پلتفرم | محدودیت | استراتژی |
|---|---|---|---|
| 1 | Render Free | ۱۵ دقیقه sleep | keepalive + health ping |
| 2 | Railway Starter | $۵ credit اول ماه | traffic gen + credit optimizer |
| 3 | Fly.io Free | ۲۵۶MB RAM, ۳GB disk | resource opt + keepalive |
| 4 | Koyeb Free | no time limit | always-on + monitoring |
| 5 | Glitch | ۵ دقیقه sleep | traffic gen + external tunnel |
| 6 | Replit | Core $۲۵/month | external tunnel + keepalive |
| 7 | SnapDeploy | ۱۵ دقیقه sleep, ۱۰۰ ساعت/ماه | traffic gen + smart schedule |
| 8 | Freestyle.sh | deploy-only, no SSH | git → API relay |
| 9 | Runloop.ai | ephemeral environments | persistent state + tunnel |
| 10 | Clever Cloud | free dev plan | keepalive + external storage |
| 11 | AlwaysData | ۱GB per-user disk | persistence bypass + tunnel |
| 12 | AwardSpace | ۱۰۰MB disk | ext storage + external tunnel |
| 13 | InfinityFree | برای وب، فقط HTTP | static + tunnel to external |
| 14 | HelioHost | real shared server | SSH + keepalive + tunnel |
| 15 | Serverix.cloud | resource محدود | cgroup bypass |
| 16 | Atyro.cloud | بررسی نشده | — |
| 17 | Lucity.cloud | بررسی نشده | — |
| 18 | Pella.app | بررسی نشده | — |
| 19 | Superserve.ai | بررسی نشده | — |

### 2️⃣ **Server-as-a-Service (بدون محدودیت معمولی sleep)**  
**ویژگی:** همیشه-on یا محدودیت کمتری دارد  

| # | پلتفرم | مزیت | نکات |
|---|---|---|---|
| 20 | Belmo.io | always-on, real VM | auto token capture |
| 21 | Stormkit.io | always-on, no sleep | — |
| 22 | Qoddi.com | real VPS, always-on | — |
| 23 | Zeabur.com | real compute, auto-deploy | keepalive (optional) |
| 24 | Encore.dev | real compute + free tier | — |
| 25 | Apply.build | real compute | — |
| 26 | Tiiny.host | real compute | — |
| 27 | Kinsta.com | free dev tier | — |
| 28 | Nhost.io | BaaS + real compute | — |
| 29 | 8base.com | BaaS + compute | — |
| 30 | Back4app.com | BaaS + compute | — |

### 3️⃣ **Free Tier Cloud VMs**  
**ویژگی:** واقعی، persistent، اما محدود به منابع یا زمان  

| # | پلتفرم | منابع رایگان | محدودیت |
|---|---|---|---|
| 31 | Oracle Cloud Free | ۲ VM ARM, ۲۴GB RAM | ۲ گیگ اینترنتی, ۲۴/۷ allowed |
| 32 | Google Cloud Free | ۳۰۰$ credit | ۱۲ ماه اول |
| 33 | AWS Free Tier | ۷۵۰ ساعت EC2 | ۱۲ ماه اول |
| 34 | Azure Free Tier | ۱۰۰$ credit | ۳۰ روز آزمایشی |
| 35 | IBM Cloud Free | ۲۵ کلاس‌های compute | منابع محدود |
| 36 | Vultr Free | $۱۰۰ credit | credit-limited |

### 4️⃣ **Micro-VM و Sandbox**  
**ویژگی:** کنترل محدود، شاید root نیست  

| # | پلتفرم | مزیت | محدودیت |
|---|---|---|---|
| 37 | GitHub Codespaces | ۶۰ ساعت/ماه | session-based |
| 38 | Gitpod | ۵۰۰ ساعت/ماه | session-based |
| 39 | Stackblitz | browser-based | no persistence |
| 40 | CodeSandbox | browser-based | no persistence |
| 41 | Dayta.io | بررسی نشده | — |

### 5️⃣ **Notebook / Jupyter**  
**ویژگی:** GPU یا compute قدرتمند, session-based  

| # | پلتفرم | منابع | محدودیت |
|---|---|---|---|
| 42 | Google Colab | T4 GPU | ۱۲ ساعت/session |
| 43 | Kaggle Notebooks | T4 x۲ GPU | ۳۰ ساعت/هفته |
| 44 | Molab.marimo.io | compute قدرتمند | session resets |
| 45 | Deepnote | compute متوسط | session-based |
| 46 | Datalore | compute متوسط | session-based |
| 47 | Gradient (Paperspace) | GPU | ۶ ساعت/session |
| 48 | SaturnCloud | GPU | ۱۰ ساعت/ماه |
| 49 | Binder | CPU only | short-lived |
| 50 | ClearML | MLOps | compute محدود |

### 6️⃣ **Serverless / Edge / Static**  
**ویژگی:** compute stateless، زمان‌سنجی شده  

| # | پلتفرم | مزیت | محدودیت |
|---|---|---|---|
| 51 | Vercel | edge functions | ۱۵s timeout |
| 52 | Netlify | serverless functions | ۱۵s timeout |
| 53 | Cloudflare Workers | KV + always-on | ۵۰ms CPU time |
| 54 | Supabase | real backend | rate limits |
| 55 | Firebase | real backend | ۱۵s timeout |
| 56 | Deno Deploy | edge compute | ۱۵s timeout |
| 57 | Wasmer.io | WASM | memory محدود |
| 58 | Fleek.sh | decentralized hosting | compute محدود |
| 59 | Qoddi.com | real compute | — (overlaps) |

### 7️⃣ **Static / No Compute**  
**ویژگی:** فقط فایل‌های استاتیک، نیاز به integration دارد  

| # | پلتفرم | زمان استفاده |
|---|---|---|
| 60 | Val.town | scripting-only |
| 61 | Codeberg.org | git hosting |
| 62 | Boxd.sh | بررسی نشده |

### 8️⃣ **Specialized MLOps / Data**  
**ویژگی:** برای ML/AI workflows، compute محدود  

| # | پلتفرم | مزیت | محدودیت |
|---|---|---|---|
| 63 | Hugging Face Spaces | Gradio + compute | always-on |
| 64 | Hopsworks.ai | MLOps | resource محدود |
| 65 | Appwrite.io | BaaS + functions | rate limits |
| 66 | Ninox.com | database + automations | limited |
| 67 | Pulumi.com | infrastructure as code | free tier |

### 9️⃣ **Tunnel / Proxy / VPN**  
**ویژگی:** برای دسترسی خارجی  

| # | سرویس | ویژگی | منبع |
|---|---|---|---|
| 68 | Cloudflare Tunnel | unlimited, free | — |
| 69 | ngrok | free tier محدود | — |
| 70 | localtunnel | free, unstable | — |
| 71 | serveo.net | free SSH tunnel | — |
| 72 | pinggy.io | ۶۰ min timeout | — |
| 73 | sshx.io | collaborative web terminal | از پروژه‌های کاربر |
| 74 | Tailscale | free 6 users | — |
| 75 | ZeroTier | free plan | — |
| 76 | frp | reverse proxy | از GitHub |

---

## 🧩 استراتژی‌های ترکیبی پلتفرم

### 🔄 **Hybrid Compute Chain**  
یک برنامه روی یک پلتفرم (مثل Render) اجرا می‌شود، خروجی یا API‌اش به‌وسیله Tunnel به یک پلتفرم دیگر (مثل HuggingFace یا Cloudflare Workers) ار سال می‌شود، سپس Cloudflare Tunnel اینترنتی می‌شود.

### ⛓️ **Tunnel Cascade**  
اگر Cloudflare Tunnel در دسترس نیست (مثل Molab)، از یک پلتفرم دیگر (Render یا Railway) برای اجرای `cloudflared tunnel` استفاده می‌کنیم تا اینترنتی شود، سپس tunnel را به سمت خود پلتفرم اول هدایت می‌کنیم.

### 🧠 **AI Model Relay**  
یک مدل LLM روی یک پلتفرم (مثل Ollama روی Molab یا HuggingFace) اجرا می‌شود، خروجی به یک API ساده روی Deno Deploy یا Vercel فرستاده می‌شود، سپس از Cloudflare Tunnel یا ngrok خارج می‌شود.

---

## 🎯 هدف نهایی

یک برنامهٔ **ماژولار، قابل ترکیب، ۱۰۰% مستند** که:
1. هر پلتفرم را تشخیص می‌دهد
2. استراتژی ترکیبی مناسب را انتخاب می‌کند
3. نصب خودکار ماژول‌های لازم
4. همه تست‌ها و نتایج در GitHub مستند می‌شوند

---

**برای مشاهدهٔ جزئیات کامل معماری، به `agent-nodii-research/ANALYSIS_PART3.md` مراجعه کنید.**