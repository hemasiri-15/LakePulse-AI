# LakePulse AI — Deployment Playbook
# Railway (backend) + Vercel (frontend)
# Estimated time: 30–45 minutes

## ── PART 1: RAILWAY (Backend + DB + Redis) ────────────────────────────────────

### Step 1 — Install Railway CLI
npm install -g @railway/cli
railway login

### Step 2 — Create project and link
cd lakepulse/backend
railway init                  # creates a new Railway project
railway link                  # or select existing project

### Step 3 — Add Postgres plugin
# In Railway dashboard → your project → "+ New" → "Database" → "Postgres"
# DATABASE_URL is injected automatically.

### Step 4 — Add Redis plugin
# Railway dashboard → "+ New" → "Database" → "Redis"
# REDIS_URL is injected automatically.

### Step 5 — Set environment variables
# Dashboard → your service → Variables → "RAW Editor", paste:

SECRET_KEY=<run: openssl rand -hex 32>
ADMIN_USER=admin
ADMIN_PASS=<your-strong-password>
IOT_API_KEYS=<generate after first deploy via /api/auth/api-key>
GHMC_WEBHOOK_URL=          # leave blank for now

### Step 6 — Deploy
railway up

# Watch logs:
railway logs --tail

### Step 7 — Verify
curl https://<your-app>.railway.app/health
# Expected: {"status":"ok","version":"1.0.0","redis":"ok","database":"ok"}

### Step 8 — Seed reference data (one-time)
# First, get an admin JWT:
curl -X POST https://<your-app>.railway.app/api/auth/token \
  -d "username=admin&password=<ADMIN_PASS>" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Copy the access_token, then seed lakes:
curl -X POST https://<your-app>.railway.app/api/admin/seed \
  -H "Authorization: Bearer <token>"

# Seed 30 days of synthetic sensor readings for demo:
curl -X POST "https://<your-app>.railway.app/api/admin/seed/readings?days=30" \
  -H "Authorization: Bearer <token>"

# Recompute health scores:
curl -X POST https://<your-app>.railway.app/api/admin/score/all \
  -H "Authorization: Bearer <token>"

### Useful Railway commands
railway status
railway logs
railway shell          # SSH into the container
railway variables      # list all env vars


## ── PART 2: VERCEL (Frontend) ─────────────────────────────────────────────────

### Step 1 — Install Vercel CLI (if not already)
npm install -g vercel

### Step 2 — Add the API base URL to your frontend
# In your React project root, create .env.production:
echo "VITE_API_URL=https://<your-app>.railway.app" > .env.production

# Update your frontend API calls to use:
const API = import.meta.env.VITE_API_URL

### Step 3 — Deploy frontend
cd ../frontend      # your React project root
vercel              # follow prompts; choose "Vite" framework preset

# Subsequent deploys:
vercel --prod

### Step 4 — Set Vercel environment variable
vercel env add VITE_API_URL production
# Enter: https://<your-app>.railway.app

### Step 5 — Tighten CORS in backend
# Once you have your Vercel URL (e.g. https://lakepulse.vercel.app),
# update main.py:
#   allow_origins=["https://lakepulse.vercel.app"]
# Then re-deploy backend: railway up


## ── PART 3: ESP32 Integration ─────────────────────────────────────────────────

### Arduino sketch snippet (paste into your ESP32 firmware):

# const char* API_URL = "https://<your-app>.railway.app/api/sensors/ingest";
# const char* API_KEY = "your-iot-api-key";   // from /api/auth/api-key
#
# // In your loop():
# StaticJsonDocument<256> doc;
# doc["lake_id"]       = 1;             // Hussain Sagar
# doc["do_mgl"]        = readDO();
# doc["ph"]            = readPH();
# doc["temp_c"]        = readTemp();
# doc["tds_ppm"]       = readTDS();
# doc["turbidity_ntu"] = readTurbidity();
# doc["source"]        = "iot";
#
# HTTPClient http;
# http.begin(API_URL);
# http.addHeader("Content-Type", "application/json");
# http.addHeader("X-API-Key", API_KEY);
# int code = http.POST(serialize(doc));
# // 201 = success


## ── PART 4: Verify full stack ─────────────────────────────────────────────────

# 1. Backend health:         https://<your-app>.railway.app/health         → {"status":"ok"}
# 2. API docs:               https://<your-app>.railway.app/docs            → Swagger UI
# 3. Lakes list:             https://<your-app>.railway.app/api/lakes       → JSON array
# 4. Latest sensor reading:  https://<your-app>.railway.app/api/sensors/1/latest
# 5. Frontend:               https://lakepulse.vercel.app                   → dashboard
